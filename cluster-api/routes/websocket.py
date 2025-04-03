from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict

router = APIRouter()

# Dictionary to manage active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Function to send a message to a specific user
async def send_message_to_user(user_id: str, message: dict):
    if user_id in active_connections:
        await active_connections[user_id].send_json(message)

# Function to broadcast a message to all connected users
async def broadcast_message(message: dict):
    for connection in active_connections.values():
        await connection.send_json(message)

@router.websocket("/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            # Process incoming data (if needed)
            print(f"Received data from {user_id}: {data}")
            # Example response
            response = {
                "user_id": user_id,
                "status": "connected",
                "user_created_cluster": data.get("user_created_cluster", "unknown")
            }
            await websocket.send_json(response)

            # Example: Emit a message to all users
            await broadcast_message({"message": f"User {user_id} sent data", "data": data})
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user: {user_id}")
        active_connections.pop(user_id, None)
