import asyncio
import functools
import json

from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed

from ..utils.signals import Signal

server_loop = asyncio.new_event_loop()
CONNECTIONS = set()
on_received_message = Signal()
on_connected = Signal()
_send_lock = None


def run_on_server_loop(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if asyncio.get_running_loop() is server_loop:
            return await func(*args, **kwargs)
        if not server_loop.is_running():
            raise RuntimeError("Start the VISYB shell with python -m visyb first.")
        future = asyncio.run_coroutine_threadsafe(func(*args, **kwargs), server_loop)
        return await asyncio.wrap_future(future)
    return wrapper


async def handler(ws):
    CONNECTIONS.add(ws)
    try:
        await send_message("CONNECTED", {}, connections=[ws])
        await on_connected.emit(ws)
        print(f"Godot client connected ({len(CONNECTIONS)} client(s)).", flush=True)
        async for string in ws:
            try:
                message = json.loads(string)
                await on_received_message.emit(ws, message)
            except Exception as error:
                print(f"[VISYB] Cannot process client message: {error}", flush=True)
    except ConnectionClosed:
        pass
    finally:
        CONNECTIONS.discard(ws)


async def start(host="localhost", port=8765):
    global _send_lock
    _send_lock = asyncio.Lock()
    return await serve(handler, host, port)


@run_on_server_loop
async def send_message(type, data, connections=None):
    # Keep chunks of different messages from interleaving on a socket.
    message = json.dumps({"type": type, "data": data}, allow_nan=False) + "\n"
    async with _send_lock:
        for conn in tuple(CONNECTIONS if connections is None else connections):
            try:
                for part in split_message(message):
                    await conn.send(part)
            except ConnectionClosed:
                CONNECTIONS.discard(conn)


def split_message(message):
    # json.dumps uses ASCII escapes, so characters and bytes have equal lengths.
    return [message[i:i + 65536] for i in range(0, len(message), 65536)]
