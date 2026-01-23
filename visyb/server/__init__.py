import asyncio
import json
from datetime import datetime
from aiohttp import web
from ..utils.signals import Signal

# global state
server_loop = asyncio.new_event_loop()
CONNECTIONS = []
CONNECTION_METADATA = {}  # Track connection details
on_received_message = Signal()

# aiohttp application
app = web.Application()

# extract real ip in order cloudflare, x-forwarded-for x-real-ip direct
def get_real_ip(request):
    if 'CF-Connecting-IP' in request.headers:
        return request.headers['CF-Connecting-IP']

    if 'X-Forwarded-For' in request.headers:
        forwarded_for = request.headers['X-Forwarded-For']
        return forwarded_for.split(',')[0].strip()

    if 'X-Real-IP' in request.headers:
        return request.headers['X-Real-IP']

    return request.remote

# handle HTTP and WebSocket(upgrade)
async def root_handler(request):
    # upgrade request
    if request.headers.get('Upgrade', '').lower() == 'websocket':
        # WebSocket connection
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # track connection
        CONNECTIONS.append(ws)

        # extract real IP address
        real_ip = get_real_ip(request)

        metadata = {
            'connected_at': datetime.now(),
            'remote_address': real_ip,
            'state': 'connected',
            'message_count': 0
        }

        if 'CF-IPCountry' in request.headers:
            metadata['country'] = request.headers['CF-IPCountry']

        CONNECTION_METADATA[id(ws)] = metadata

        # send connected message \n for godot required
        connected_msg = json.dumps({"type": "CONNECTED", "data": {}}) + "\n"
        await ws.send_str(connected_msg)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        CONNECTION_METADATA[id(ws)]['message_count'] += 1
                        CONNECTION_METADATA[id(ws)]['last_message'] = datetime.now()
                        await on_received_message.emit(ws, data)
                    except Exception as err:
                        print(f"[ERROR] While processing incoming message: {err}")
                elif msg.type == web.WSMsgType.ERROR:
                    print(f'WebSocket error: {ws.exception()}')
        finally:
            CONNECTIONS.remove(ws)
            if id(ws) in CONNECTION_METADATA:
                del CONNECTION_METADATA[id(ws)]

        return ws
    else:
        # normal http
        from .dashboard import get_dashboard_html
        html = get_dashboard_html()
        return web.Response(text=html, content_type='text/html')


async def _send_message_async(type, data, connections=None):
    if connections is None:
        connections = CONNECTIONS

    message = json.dumps({"type": type, "data": data})

    # split message if too large
    message_parts = split_message(message + "\n")

    disconnected = []
    for ws in connections:
        if not ws.closed:
            try:
                for part in message_parts:
                    await ws.send_str(part)
                print(f"[INFO] Sent {type} message to client")
            except Exception as err:
                print(f"[ERROR] Sending message to client: {err}")
                disconnected.append(ws)

    # clean up disconnected
    for ws in disconnected:
        if ws in CONNECTIONS:
            CONNECTIONS.remove(ws)


# send message ot websocket clients
def send_message(type, data, connections=None):
    try:
        if not server_loop.is_running():
            print(f"[WARN] Server loop not running, cannot send {type} message")
            return None

        future = asyncio.run_coroutine_threadsafe(
            _send_message_async(type, data, connections),
            server_loop
        )
        return future
    except Exception as err:
        print(f"[ERROR] Scheduling message send: {err}")
        return None

#split larget messages
def split_message(msg: str):
    MAX_LEN = 2**16  # 64KB
    parts = []
    for i in range(0, len(msg), MAX_LEN):
        parts.append(msg[i:i+MAX_LEN])
    return parts

# start server
async def start():
    from .dashboard import setup_dashboard_routes

    # setup API routes
    setup_dashboard_routes(app)

    # root path handles both HTTP and WebSocket
    app.router.add_get('/', root_handler)

    # start server on port 8765 (0.0.0.0 for external access)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8765)
    await site.start()

    print("VISYB Unified Server Running on 0.0.0.0:8765")
    print("\n")
    print(f"Dashboard (HTTP):    http://0.0.0.0:8765/")
    print(f"WebSocket:           ws://0.0.0.0:8765/")
    print(f"API Status:          http://0.0.0.0:8765/api/status")
    print(f"API Plots:           http://0.0.0.0:8765/api/plots")
    print(f"API Connections:     http://0.0.0.0:8765/api/connections")
    print(f"Godot Web App:       http://0.0.0.0:8765/app/")
    print("\n")

    # keep running forever
    await asyncio.Future()
