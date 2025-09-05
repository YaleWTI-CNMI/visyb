from visyb.processor.definitions import Graph3DPlot
from visyb.processor.__runtime__ import add_plot
import math

# node move callback example how to use the node position update callbacks
def node_moved_callback(node_id, x, y, z):
    """Callback function that gets called when a node is moved in VR"""
    print(f"Node {node_id} moved to position: ({x:.2f}, {y:.2f}, {z:.2f})")

# create a graph with interactive nodes (callbacks)
async def create_interactive_graph():

    # create the graph and toggle movable_nodes to True
    graph = Graph3DPlot(movable_nodes=True)
    
    # Create nodes with movement callbacks
    for i in range(6):
        angle = 2 * math.pi * i / 6
        x = math.cos(angle) * 3
        y = math.sin(angle) * 3
        z = 0
        
        graph.add_node(
            id=i,
            x=x, y=y, z=z,
            label=f"Interactive Node {i}",
            color={'r': 0.3 + i*0.1, 'g': 0.7, 'b': 0.9},
            size=1.0,
            movable=True,
            on_move=node_moved_callback
        )
    
    # edges
    for i in range(6):
        next_node = (i + 1) % 6
        graph.add_edge(
            source_id=i,
            target_id=next_node,
            color={'r': 0.4, 'g': 0.8, 'b': 0.4},
            width=2.0
        )
    
    # center node with different callback
    def center_node_callback(node_id, x, y, z):
        print(f"CENTER NODE {node_id} moved! New position: ({x:.2f}, {y:.2f}, {z:.2f})")
        print("This could trigger a re-layout of the entire graph!")
    
    graph.add_node(
        id='center',
        x=0, y=0, z=0,
        label="Center Hub",
        color={'r': 1.0, 'g': 0.5, 'b': 0.2},
        size=1.5,
        movable=True,
        on_move=center_node_callback
    )
    
    # connect center to all other nodes
    for i in range(6):
        graph.add_edge(
            source_id='center',
            target_id=i,
            color={'r': 0.8, 'g': 0.3, 'b': 0.3},
            width=1.0
        )
    
    return graph

#   main function for interactive graph

async def main():
    print("Creating interactive 3D graph with node movement callbacks...")
    
    # create graph
    interactive_graph = await create_interactive_graph()
    
    # add to the visualization system
    await add_plot(interactive_graph)

if __name__ == "__main__":
    main()