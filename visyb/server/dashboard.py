import os
import json
from datetime import datetime
from aiohttp import web
from . import CONNECTIONS, CONNECTION_METADATA

# setup dashboard api routes
def setup_dashboard_routes(app):
    app.router.add_get('/api/status', api_status)
    app.router.add_get('/api/plots', api_plots)
    app.router.add_get('/api/connections', api_connections)
    app.router.add_post('/api/add_plot', api_add_plot)

    godot_export_path = os.path.join(os.path.dirname(__file__), '..', '..', 'godot_export')
    if os.path.exists(godot_export_path):
        app.router.add_static('/app', godot_export_path)
        print(f"Serving Godot app from {godot_export_path}")

# api status handler
async def api_status(request):
    from ..processor.__runtime__ import PLOTS

    status = {
        'server_running': True,
        'port': 8765,
        'total_plots': len(PLOTS),
        'active_connections': len(CONNECTIONS),
        'timestamp': datetime.now().isoformat()
    }

    return web.json_response(status)

# api get plots
async def api_plots(request):
    from ..processor.__runtime__ import PLOTS

    plots_info = []
    for plot_id, plot in PLOTS.items():
        plot_info = {
            'id': plot_id,
            'type': type(plot).__name__,
        }

        if hasattr(plot, 'result'):
            result = plot.result
            plot_info['result_type'] = type(result).__name__

            if hasattr(plot, 'mods'):
                modifiers = {}
                for mod_name, mod_data in plot.mods.items():
                    modifiers[mod_name] = {
                        'value': mod_data.get('value'),
                        'type': type(mod_data.get('definition')).__name__ if mod_data.get('definition') else 'unknown'
                    }
                plot_info['modifiers'] = modifiers

        plots_info.append(plot_info)

    return web.json_response(plots_info)

# api get connections
async def api_connections(request):
    connections_info = []

    for i, conn in enumerate(CONNECTIONS):
        conn_id = id(conn)
        metadata = CONNECTION_METADATA.get(conn_id, {})

        conn_info = {
            'id': i,
            'remote_address': str(metadata.get('remote_address', 'unknown')),
            'state': metadata.get('state', 'unknown'),
            'message_count': metadata.get('message_count', 0),
            'connected_at': metadata.get('connected_at').isoformat() if metadata.get('connected_at') else None,
        }

        if 'last_message' in metadata:
            conn_info['last_message'] = metadata['last_message'].isoformat()
        if 'country' in metadata:
            conn_info['country'] = metadata['country']

        connections_info.append(conn_info)

    return web.json_response({
        'total': len(CONNECTIONS),
        'connections': connections_info
    })

# api add plot
async def api_add_plot(request):
    from ..processor.__runtime__ import add_plot

    try:
        plot_data = await request.json()

        # TODO: reconstruct plot from serialized data
        # For now, return an error
        return web.json_response({
            'error': 'Not implemented yet.'
        }, status=501)

    except Exception as e:
        return web.json_response({
            'error': str(e)
        }, status=400)


# dashboard html
def get_dashboard_html():
    # TODO: use template file
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VISYB Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
        }

        h1 {
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #666;
            font-size: 1.1em;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .stat-value {
            color: #333;
            font-size: 2.5em;
            font-weight: bold;
        }

        .section {
            background: rgba(255, 255, 255, 0.95);
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }

        h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .plot-item, .connection-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }

        .plot-header, .connection-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .plot-id, .connection-id {
            font-weight: bold;
            color: #667eea;
            font-size: 1.1em;
        }

        .plot-type, .connection-status {
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
        }

        .modifiers {
            margin-top: 10px;
            padding: 10px;
            background: white;
            border-radius: 5px;
        }

        .modifier-item {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            color: #555;
        }

        .modifier-name {
            font-weight: 500;
        }

        .modifier-value {
            color: #667eea;
            font-family: monospace;
        }

        .connection-details {
            font-size: 0.9em;
            color: #666;
            margin-top: 8px;
        }

        .connection-details div {
            margin: 4px 0;
        }

        .empty-state {
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }

        .timestamp {
            color: #999;
            font-size: 0.9em;
            text-align: right;
            margin-top: 20px;
        }

        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.2s;
        }

        .refresh-btn:hover {
            background: #5568d3;
        }

        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #4caf50;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><span class="status-indicator"></span>VISYB Dashboard</h1>
            <p class="subtitle">Real-time monitoring of plots and connections on port 8765</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Plots</div>
                <div class="stat-value" id="total-plots">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Connections</div>
                <div class="stat-value" id="active-connections">-</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Server Port</div>
                <div class="stat-value">8765</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Protocol</div>
                <div class="stat-value" style="font-size: 1.5em;">HTTP+WS</div>
            </div>
        </div>

        <div class="section">
            <h2>
                <span>Plots</span>
                <button class="refresh-btn" onclick="refreshData()">Refresh</button>
            </h2>
            <div id="plots-container"></div>
        </div>

        <div class="section">
            <h2>WebSocket Connections</h2>
            <div id="connections-container"></div>
        </div>

        <div class="timestamp" id="last-update"></div>
    </div>

    <script>
        async function fetchStatus() {
            const response = await fetch('/api/status');
            return await response.json();
        }

        async function fetchPlots() {
            const response = await fetch('/api/plots');
            return await response.json();
        }

        async function fetchConnections() {
            const response = await fetch('/api/connections');
            return await response.json();
        }

        function renderPlots(plots) {
            const container = document.getElementById('plots-container');

            if (plots.length === 0) {
                container.innerHTML = '<div class="empty-state">No plots available</div>';
                return;
            }

            container.innerHTML = plots.map(plot => `
                <div class="plot-item">
                    <div class="plot-header">
                        <span class="plot-id">Plot #${plot.id}</span>
                        <span class="plot-type">${plot.result_type || plot.type}</span>
                    </div>
                    ${plot.modifiers ? `
                        <div class="modifiers">
                            <strong>Modifiers:</strong>
                            ${Object.entries(plot.modifiers).map(([name, data]) => `
                                <div class="modifier-item">
                                    <span class="modifier-name">${name}</span>
                                    <span class="modifier-value">${JSON.stringify(data.value)}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('');
        }

        function renderConnections(data) {
            const container = document.getElementById('connections-container');

            if (data.total === 0) {
                container.innerHTML = '<div class="empty-state">No active connections</div>';
                return;
            }

            container.innerHTML = data.connections.map(conn => `
                <div class="connection-item">
                    <div class="connection-header">
                        <span class="connection-id">Connection #${conn.id}${conn.country ? ` (${conn.country})` : ''}</span>
                        <span class="connection-status">${conn.state}</span>
                    </div>
                    <div class="connection-details">
                        <div><strong>Remote:</strong> ${conn.remote_address}${conn.country ? ` [${conn.country}]` : ''}</div>
                        <div><strong>Connected:</strong> ${conn.connected_at ? new Date(conn.connected_at).toLocaleString() : 'Unknown'}</div>
                        <div><strong>Messages:</strong> ${conn.message_count}</div>
                        ${conn.last_message ? `<div><strong>Last Message:</strong> ${new Date(conn.last_message).toLocaleString()}</div>` : ''}
                    </div>
                </div>
            `).join('');
        }

        async function refreshData() {
            try {
                const [status, plots, connections] = await Promise.all([
                    fetchStatus(),
                    fetchPlots(),
                    fetchConnections()
                ]);

                document.getElementById('total-plots').textContent = status.total_plots;
                document.getElementById('active-connections').textContent = status.active_connections;

                renderPlots(plots);
                renderConnections(connections);

                document.getElementById('last-update').textContent =
                    `Last updated: ${new Date().toLocaleString()}`;
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        }

        // initial load
        refreshData();

        // refresh every 5 seconds
        setInterval(refreshData, 5000);
    </script>
</body>
</html>
"""
