"""
WebSocket client to receive cluster status updates and send messages.

Connects to the server, handles incoming messages, and optionally sends periodic pings.
"""

# import argparse
# import asyncio
# import json
# import signal
# import sys
# import time
# from datetime import datetime

# import websockets

# # Flag to control the main loop
# running = True


# def handle_signal(sig, frame):
#     """Handle interrupt signal to allow graceful shutdown."""
#     global running
#     print("\nShutting down...")
#     running = False


# # Register signal handlers
# signal.signal(signal.SIGINT, handle_signal)
# signal.signal(signal.SIGTERM, handle_signal)


# def format_message(message_data):
#     """Format a received message for display."""
#     try:
#         if isinstance(message_data, str):
#             data = json.loads(message_data)
#         else:
#             data = message_data

#         event_type = data.get("event", "unknown")
#         timestamp = data.get("timestamp", datetime.now().isoformat())

#         if event_type == "cluster_status_updated":
#             return f"[{timestamp}] CLUSTER UPDATE: {data.get('cluster_name', 'unknown')} (ID: {data.get('cluster_id', 'unknown')}) is now {data.get('status', 'unknown')}"
#         elif event_type == "connection_established":
#             return f"[{timestamp}] CONNECTION ESTABLISHED: {data.get('message', '')}"
#         elif event_type == "message_received":
#             return f"[{timestamp}] MESSAGE ACKNOWLEDGED: Server received {json.dumps(data.get('data_received', {}))}"
#         else:
#             return f"[{timestamp}] {json.dumps(data)}"
#     except Exception as e:
#         return f"Error formatting message: {str(e)}\nRaw message: {message_data}"


# async def send_periodic_ping(websocket, interval=30):
#     """Send periodic ping messages to keep the connection alive."""
#     while running:
#         try:
#             await asyncio.sleep(interval)
#             if not running:
#                 break

#             ping_message = {"type": "ping", "timestamp": datetime.now().isoformat()}
#             await websocket.send(json.dumps(ping_message))
#             print(f"Ping sent at {datetime.now().isoformat()}")
#         except Exception as e:
#             if running:
#                 print(f"Error sending ping: {str(e)}")
#             break


# async def test_websocket(user_id, server_url, keep_alive=True):
#     """Connect to WebSocket server and handle messages."""
#     uri = f"{server_url}/v1/websocket/{user_id}"

#     print(f"Connecting to {uri} as user {user_id}...")
#     try:
#         async with websockets.connect(uri, ping_interval=60) as websocket:
#             print(f"Connected to WebSocket server as user {user_id}!")

#             # Start ping task if keep_alive is True
#             ping_task = None
#             if keep_alive:
#                 ping_task = asyncio.create_task(send_periodic_ping(websocket))

#             # Send initial message
#             initial_message = {
#                 "message": "Hello from client",
#                 "user_id": user_id,
#                 "client_timestamp": datetime.now().isoformat(),
#             }
#             await websocket.send(json.dumps(initial_message))
#             print(f"Sent initial message: {json.dumps(initial_message)}")

#             # Listen for messages
#             while running:
#                 try:
#                     response = await websocket.recv()
#                     formatted = format_message(response)
#                     print(formatted)
#                 except websockets.exceptions.ConnectionClosed:
#                     print("Connection closed by server")
#                     break
#                 except Exception as e:
#                     print(f"Error receiving message: {str(e)}")
#                     if not running:
#                         break
#                     await asyncio.sleep(1)

#             # Cancel ping task
#             if ping_task:
#                 ping_task.cancel()

#     except Exception as e:
#         print(f"Connection error: {str(e)}")


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description="WebSocket Client for Cluster Status Updates"
#     )
#     parser.add_argument(
#         "--user", "-u", default="test-user", help="User ID to connect with"
#     )
#     parser.add_argument(
#         "--server", "-s", default="ws://localhost:8000", help="WebSocket server URL"
#     )
#     parser.add_argument(
#         "--no-ping", action="store_true", help="Disable periodic ping messages"
#     )

#     args = parser.parse_args()

#     try:
#         asyncio.run(test_websocket(args.user, args.server, not args.no_ping))
#     except KeyboardInterrupt:
#         print("Interrupted by user")
