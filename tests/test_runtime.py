import asyncio
import json
import threading

import pytest
from websockets.asyncio.client import connect

from visyb import server
from visyb.processor import __runtime__ as runtime
from visyb.processor.definitions import BuilderPlot, Model3DPlot, modcont, plot_generator


@pytest.fixture
def running_server():
    server.server_loop = asyncio.new_event_loop()
    runtime.PLOTS.clear()
    server.CONNECTIONS.clear()
    thread = threading.Thread(target=server.server_loop.run_forever)
    thread.start()
    listener = None
    try:
        listener = asyncio.run_coroutine_threadsafe(server.start('127.0.0.1', 0), server.server_loop).result(5)
        yield f'ws://127.0.0.1:{listener.sockets[0].getsockname()[1]}'
    finally:
        if listener is not None:
            async def stop():
                listener.close()
                await listener.wait_closed()
            asyncio.run_coroutine_threadsafe(stop(), server.server_loop).result(5)
        server.server_loop.call_soon_threadsafe(server.server_loop.stop)
        thread.join(5)
        server.server_loop.close()
        runtime.PLOTS.clear()


async def receive(ws):
    buffer = ''
    while not buffer.endswith('\n'):
        buffer += await asyncio.wait_for(ws.recv(), 5)
    return json.loads(buffer)


@plot_generator
def adjustable(frame: modcont(range=[1, 150]) = 62):
    plot = BuilderPlot([-1, 1], [-1, 1], [-1, 1])
    plot.add_point_set([frame / 150], [0], [0])
    return plot


def test_modifier_instances_and_explicit_arguments():
    first, second = adjustable(40), adjustable(frame=90)
    first.update_mod('frame', 75)
    assert first.mods['frame']['value'] == 75
    assert second.mods['frame']['value'] == 90
    assert adjustable().mods['frame']['value'] == 62
    assert next(iter(first.result.objects.values()))['x'] == [0.5]


def test_shell_send_replay_update_and_clear(running_server):
    async def scenario():
        id = await runtime.add_plot(adjustable())
        async with connect(running_server) as ws:
            assert (await receive(ws))['type'] == 'CONNECTED'
            assert (await receive(ws))['data']['id'] == id
            await ws.send(json.dumps({'type': 'UPDATE_MODS', 'data': {'id': id, 'mods': {'frame': 97}}}))
            update = await receive(ws)
            assert update['type'] == 'PLOT_UPDATED'
            assert update['data']['mods']['frame']['value'] == 97
        async with connect(running_server) as ws:
            await receive(ws)
            replay = await receive(ws)
            assert replay['data']['mods']['frame']['value'] == 97
            await runtime.clear_plots()
            assert (await receive(ws)) == {'type': 'PLOT_REMOVED', 'data': {'id': id}}
            assert not runtime.PLOTS
    asyncio.run(scenario())


def test_large_messages_and_point_callback(running_server):
    payload = 'v 0 0 0\n' * 30000
    @plot_generator
    def model():
        return Model3DPlot(payload, 'obj')
    @plot_generator
    def clickable():
        plot = BuilderPlot([-1, 1], [-1, 1], [-1, 1])
        plot.add_point_set([0], [0], [0], onclick=lambda index: asyncio.create_task(runtime.add_plot(model())))
        return plot
    async def scenario():
        async with connect(running_server) as ws:
            await receive(ws)
            await runtime.add_plot(clickable())
            point = next(iter((await receive(ws))['data']['result']['objects'].values()))
            await ws.send(json.dumps({'type': 'VRID_CALL', 'data': {'vrid': point['vrid'], 'args': {'action': 'point_pressed', 'index': 0}}}))
            message = await receive(ws)
            assert message['data']['result']['data'] == payload
            await asyncio.gather(runtime.add_plot(model()), runtime.add_plot(model()))
            for _ in range(2):
                assert (await receive(ws))['data']['result']['data'] == payload
    asyncio.run(scenario())


def test_malformed_input_does_not_break_connection(running_server):
    async def scenario():
        async with connect(running_server) as ws:
            await receive(ws)
            await ws.send('invalid json')
            await runtime.add_plot(adjustable())
            assert (await receive(ws))['type'] == 'PLOT_ADDED'
    asyncio.run(scenario())
