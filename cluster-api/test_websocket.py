import asyncio
import websockets
import json
import sys

async def test_websocket():
    # Update with your actual WebSocket URL
    uri = "ws://zerone-4409-9534.01cloud.com/v1/websocket/2a754dd2-db9e-4432-999c-d44a075e5dc3"
    
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri, ping_interval=None) as websocket:
            print("Connected to WebSocket server!")
            
            # Send a test message
            message = {
                "message": "Hello from client",
                "user_created_cluster": "test_cluster"
            }
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}")
            
            # Wait for response
            response = await websocket.recv()
            print(f"Received: {response}")
            
            # Keep connection open to receive broadcast messages
            print("Waiting for messages (press Ctrl+C to exit)...")
            while True:
                try:
                    response = await websocket.recv()
                    print(f"Received broadcast: {response}")
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break
    except Exception as e:
        print(f"Error: {str(e)}")
        return

if __name__ == "__main__":
    asyncio.run(test_websocket())
