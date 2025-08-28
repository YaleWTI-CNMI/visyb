import asyncio
import websockets.protocol
from websockets.server import serve
import websockets
import json
import functools
from ..utils.signals import Signal

server_loop = asyncio.new_event_loop()
CONNECTIONS = []
on_received_message = Signal()

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
        async for string in ws:
            try:
                message = json.loads(string)
                await on_received_message.emit(ws, message)
            except Exception as err:
                print(f"[ERR] While processing incoming message [{message}]: {err}")
                json.JSONDecodeError

        await ws.wait_closed()
    finally:
        CONNECTIONS.remove(ws)


async def start():
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


@run_on_server_loop
async def send_message(type, data, connections=CONNECTIONS):
    s = json.dumps({"type": type, "data": data}) + "\n" # newline is the designated message terminator
    s_splits = split_message(s)
    for conn in connections:
        for part in s_splits:
            await conn.send(part)

def split_message(msg: str):
    MAX_LEN = 2**16 # in bytes
    parts = []
    for i in range(0, len(msg), MAX_LEN):
        parts.append(msg[i:i+MAX_LEN])
    return parts