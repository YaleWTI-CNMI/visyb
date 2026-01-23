#Example that send plot to VISYB server from a Python client

import math
import asyncio
from asyncio import sleep

import websockets
import json


def create_spiral_sphere_data(turns=10, points_per_turn=20):
    points = []
    num_points = turns * points_per_turn
    radius = 8.0

    for i in range(num_points):
        t = (i / num_points) * turns * 2 * math.pi
        phi = (i / num_points) * math.pi

        x = radius * math.sin(phi) * math.cos(t)
        y = radius * math.sin(phi) * math.sin(t)
        z = radius * math.cos(phi)

        points.append((x, y, z))

    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    z_coords = [p[2] for p in points]

    colors = []
    for i in range(len(points)):
        t = i / len(points)
        hue = t * 360
        if hue < 120:
            r, g, b = 1 - hue/120, hue/120, 0
        elif hue < 240:
            r, g, b = 0, 1 - (hue-120)/120, (hue-120)/120
        else:
            r, g, b = (hue-240)/120, 0, 1 - (hue-240)/120

        colors.append({'r': r, 'g': g, 'b': b})

    sizes = [0.5 for _ in points]  # Bigger points

    plot_data = {
        "type": "builder",
        "mods": {},  # Empty modifiers for now
        "result": {
            "type": "builder",
            "xlim": [-5, 5],
            "ylim": [-5, 5],
            "zlim": [-5, 5],
            "objects": {
                "spiral_sphere": {
                    "type": "point_set",
                    "x": x_coords,
                    "y": y_coords,
                    "z": z_coords,
                    "xlim": [-5, 5],
                    "ylim": [-5, 5],
                    "zlim": [-5, 5],
                    "color": colors,
                    "size": sizes,
                    "vrid": 0
                }
            }
        }
    }

    return plot_data



async def send_plot_to_server():
    server_url = "ws://localhost:8765"

    # prepare spiral spheres data
    plot_data = create_spiral_sphere_data(turns=10, points_per_turn=20)
    num_points = len(plot_data["result"]["objects"]["spiral_sphere"]["x"])

    # send plot
    try:
        async with websockets.connect(server_url) as websocket:

            connected_msg = await websocket.recv()
            data = json.loads(connected_msg.strip())
            message = {
                "type": "ADD_PLOT",
                "data": plot_data
            }
            await websocket.send(json.dumps(message) + "\n")
            await sleep(10)
            print("Plot sent.")

    except ConnectionRefusedError:
        print("[ERROR] Could not connect to server. Connection refused.")
    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    asyncio.run(send_plot_to_server())


if __name__ == "__main__":
    main()
