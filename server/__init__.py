import asyncio
import websockets.protocol
from websockets.server import serve
import websockets
import json
import functools

server_loop = asyncio.new_event_loop()
CONNECTIONS = []


def run_on_server_loop(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        async def awaitable():
            future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), server_loop)
            return await asyncio.wrap_future(future)
        return awaitable()
    return wrapper

async def handler(ws):
    CONNECTIONS.append(ws)
    await send_message("CONNECTED", {}, connections=[ws])
    try:
        # while ws.state == websockets.protocol.State.OPEN:
        #     await ws.drain()

        await ws.wait_closed()
    finally:
        CONNECTIONS.remove(ws)


async def start():
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


@run_on_server_loop
async def send_message(type, data, connections=CONNECTIONS):
    s = json.dumps({"type": type, "data": data})
    for conn in connections:
        await conn.send(s)