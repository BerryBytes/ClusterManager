from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from typing import Dict, Optional
import logging
import json
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("websocket")

router = APIRouter()

# Dictionary to manage active WebSocket connections with last activity timestamp
active_connections: Dict[str, Dict[str, any]] = {}

# Function to send a message to a specific user with retry
async def send_message_to_user(user_id: str, message: dict, retries: int = 2) -> bool:
    """Send a message to a specific user with automatic retries.
    
    Args:
        user_id: The user ID to send the message to
        message: The message payload as a dictionary
        retries: Number of retry attempts if sending fails
        
    Returns:
        bool: True if message was sent successfully, False otherwise
    """
    if not user_id:
        logger.warning(f"Cannot send message - user_id is empty")
        return False
        
    if user_id not in active_connections:
        logger.info(f"User {user_id} not connected, message not sent: {message}")
        return False
        
    for attempt in range(retries + 1):
        try:
            websocket = active_connections[user_id]["connection"]
            await websocket.send_json(message)
            
            # Update last activity timestamp
            active_connections[user_id]["last_active"] = datetime.now()
            
            logger.info(f"Successfully sent message to user {user_id}")
            return True
        except Exception as e:
            if attempt < retries:
                logger.warning(f"Attempt {attempt+1} failed to send message to {user_id}: {str(e)}. Retrying...")
                await asyncio.sleep(0.5)  # Wait before retry
            else:
                logger.error(f"Failed to send message to {user_id} after {retries+1} attempts: {str(e)}")
                # Remove dead connection
                active_connections.pop(user_id, None)
                return False
    
    return False

# Send message to multiple users efficiently
async def broadcast_to_users(user_ids: list, message: dict) -> Dict[str, bool]:
    """Send a message to multiple users efficiently.
    
    Args:
        user_ids: List of user IDs to send the message to
        message: The message payload as a dictionary
        
    Returns:
        dict: Dictionary of user_id to success/failure status
    """
    if not user_ids:
        return {}
        
    # Create tasks for all users
    tasks = {user_id: asyncio.create_task(send_message_to_user(user_id, message)) 
             for user_id in user_ids if user_id}
    
    # Wait for all tasks to complete
    results = {}
    for user_id, task in tasks.items():
        try:
            results[user_id] = await task
        except Exception as e:
            logger.error(f"Error in broadcast to {user_id}: {str(e)}")
            results[user_id] = False
            
    return results

# Function to broadcast a message to all connected users
async def broadcast_message(message: dict) -> int:
    """Broadcast a message to all connected users.
    
    Args:
        message: The message payload as a dictionary
        
    Returns:
        int: Number of successful deliveries
    """
    success_count = 0
    failed_connections = []
    
    for user_id, conn_info in active_connections.items():
        try:
            await conn_info["connection"].send_json(message)
            active_connections[user_id]["last_active"] = datetime.now()
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to broadcast to {user_id}: {str(e)}")
            failed_connections.append(user_id)
    
    # Clean up failed connections
    for user_id in failed_connections:
        active_connections.pop(user_id, None)
        
    return success_count

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint handler for user connections."""
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
        
    # Accept the connection
    await websocket.accept()
    logger.info(f"WebSocket connection established for user: {user_id}")
    
    # Store connection with timestamp
    active_connections[user_id] = {
        "connection": websocket,
        "last_active": datetime.now()
    }
    
    # Send initial connection confirmation
    try:
        welcome_message = {
            "event": "connection_established",
            "user_id": user_id,
            "message": "Connected to cluster status updates",
            "timestamp": datetime.now().isoformat(),
            "connection_count": len(active_connections)
        }
        await websocket.send_json(welcome_message)
    except Exception as e:
        logger.error(f"Error sending initial message: {str(e)}")
    
    # Handle incoming messages
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()
            logger.info(f"Received data from {user_id}: {data}")
            
            # Update activity timestamp
            active_connections[user_id]["last_active"] = datetime.now()
            
            # Send acknowledgment
            response = {
                "event": "message_received",
                "user_id": user_id,
                "status": "connected",
                "timestamp": datetime.now().isoformat(),
                "data_received": data
            }
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user_id}")
        active_connections.pop(user_id, None)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON received from {user_id}")
        active_connections.pop(user_id, None)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        active_connections.pop(user_id, None)
