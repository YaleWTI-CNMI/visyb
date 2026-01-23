"""
Simple test script to verify VISYB server functionality
No external data required

USAGE - Method 1 (interactive shell):
1. Start VISYB server: python -m visyb
2. In the IPython shell, run: %run examples/simple_test.py

USAGE - Method 2 (WebSocket Client):
1. Start VISYB server: python -m visyb
2. In another terminal: python examples/client_plot_test.py

This creates a circular pattern of points and adds it to the server.
All connected clients (VR, web, etc.) will see the plot.
"""

from visyb.processor import plot_generator, BuilderPlot, modcont
from visyb.processor.__runtime__ import add_plot


@plot_generator
def simple_plot(
    point_count: modcont(range=[5, 50], step=5) = 10,
    z_height: modcont(range=[0, 10], step=1) = 5
):
    import math

    # create circular pattern
    points = []
    for i in range(int(point_count)):
        angle = (i / point_count) * 2 * math.pi
        x = math.cos(angle) * 5
        y = math.sin(angle) * 5
        z = z_height
        points.append((x, y, z))

    plot = BuilderPlot(
        xlim=[-10, 10],
        ylim=[-10, 10],
        zlim=[0, 10]
    )

    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    z_coords = [p[2] for p in points]

    colors = [{'r': 1.0, 'g': 0.5, 'b': 0.2} for _ in points]
    sizes = [0.5 for _ in points]

    plot.add_point_set(
        x=x_coords,
        y=y_coords,
        z=z_coords,
        color=colors,
        size=sizes
    )

    print(f"Created plot with {point_count} points at height {z_height}")
    return plot


print("Creating simple test plot...")
plot = simple_plot()

print("Adding plot to server...")
add_plot(plot)

print(" Plot added successfully!")
print(f" Plot ID: {plot.id}")
