import websockets
import json
import asyncio

# Define the host and port for the WebSocket server - Currently set to localhost and port 8765.  Will be changed when VPS is deployed.
HOST = '127.0.0.1'
PORT = 8765

connections = {}

# Handles Client.py connecting to the server and registering itself
async def handle_client(websocket):
    backend_id = None

    try:
        raw = await websocket.recv()
        message = json.loads(raw)

        # Check for valid message type - "register"... simple I know
        if message.get("type") != "register":
            print("Invalid registration message received. Closing connection...")
            await websocket.close()
            return

        # Check for backend_id in the registration message
        backend_id = message.get("backend_id")
        if not backend_id:
            print("[-] No backend_id provided in registration message. Closing connection...")
            await websocket.close()
            return

        # Check for duplicate backend_id
        if backend_id in connections:
            print(f"[-] Duplicate backend_id '{backend_id}' detected. Closing connection...")
            await connections[backend_id].close()
            return
        # Registration finished server-side
        print(f"[+] Backend '{backend_id}' registered successfully.")

        # Send confirmation to client
        await websocket.send(json.dumps({
            "type": "registered",
            "backend_id": backend_id
        }))
        