import asyncio
import json
import websockets
from .processor.__runtime__ import to_client_dict

# visyb client for python
class VisybClient:

    def __init__(self, server_url="ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.connected = False

    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True

            msg = await self.websocket.recv()
            data = json.loads(msg.strip())

            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("Disconnected from server")

    async def send_plot(self, plot):
        if not self.connected:
            raise RuntimeError("[ERROR] Not connected to server.")

        plot_data = to_client_dict(plot)

        # send ADD_PLOT message
        message = {
            "type": "ADD_PLOT",
            "data": plot_data
        }

        await self.websocket.send(json.dumps(message) + "\n")

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()


# synchronous wrapper for easier use
class VisybClientSync:

    def __init__(self, server_url="ws://localhost:8765"):
        self.server_url = server_url
        self._client = None

    def __enter__(self):
        self._client = VisybClient(self.server_url)
        asyncio.run(self._client.connect())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            asyncio.run(self._client.disconnect())

    def send_plot(self, plot):
        if not self._client:
            raise RuntimeError("[ERROR] Client not initialized")
        asyncio.run(self._client.send_plot(plot))
