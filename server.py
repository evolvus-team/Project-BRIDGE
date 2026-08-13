import websockets
import json
import asyncio

# Define the host and port for the WebSocket server - Currently set to localhost and port 8765.  Will be changed when VPS is deployed.
HOST = '127.0.0.1'
PORT = 8765

connections = {}

