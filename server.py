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

        async for raw in websocket:
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                print(f"[-] Received invalid JSON message from {backend_id}. Ignoring...")
                continue

            destination = message.get("to")

            if not destination:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": "No destination provided"
                }))
                print(f"[-] No destination provided in message from {backend_id}. Ignoring...")
                continue

            target = connections.get(destination)
            if target is None:
                await websocket.send(json.dumps({
                    "type": "error",
                    "message": f"Destination '{destination}' not found"
                }))
                print(f"[-] Destination '{destination}' not found for message from {backend_id}. Ignoring...")
                continue

            message["from"] = backend_id
            await target.send(json.dumps(message))

            print(
                f"[>] {backend_id} -> {destination} "
                f"({message.get('type', 'unknown')})"
            )

    except websockets.exceptions.ConnectionClosed:
        pass

    except Exception as error:
        print(f"[!] Error handling client {backend_id}: {error}")
    finally:
        if backend_id and connections.get(backend_id) is websocket:
            del connections[backend_id]
            print(f"[-] Backend '{backend_id}' disconnected and removed from connections.")
            if backend_id:
                print(f"[!] Backend '{backend_id}' disconnected unexpectedly.")


async def main():
    print(f"Oriject BRIDGE Websocket Relay")
    print(f"Listening on {HOST}:{PORT}...")
    async with websockets.serve(handle_client, HOST, PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())