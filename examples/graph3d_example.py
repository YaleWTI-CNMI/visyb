from visyb.processor import plot_generator, modcont, modcat, modbool
from visyb.processor.definitions import Graph3DPlot
from visyb.processor.__runtime__ import add_plot
import math


#Create a simple 3d graph with interactive node count
@plot_generator
def simple_graph(num_nodes):
    """Create a simple 3D graph with interactive node count"""
    graph = Graph3DPlot()
    
    # circle pattern with some z
    for i in range(int(num_nodes)):
        angle = 2 * math.pi * i / num_nodes
        x = math.cos(angle) * 2
        y = math.sin(angle) * 2
        z = math.sin(angle * 2) * 1  # Some Z variation
        
        graph.add_node(
            id=i,
            x=x, y=y, z=z,
            label=f"Node {i}",
            color={'r': 0.2 + i/num_nodes, 'g': 0.5, 'b': 1.0},
            size=0.8 + (i % 3) * 0.4
        )
    
    # add edges to form a loop
    for i in range(int(num_nodes)):
        next_node = (i + 1) % int(num_nodes)
        graph.add_edge(
            source_id=i,
            target_id=next_node,
            color={'r': 0.3, 'g': 0.7, 'b': 0.3},
            width=1.5
        )
    
    # add 2 cross connections
    if num_nodes >= 5:
        graph.add_edge(0, 2, color={'r': 1.0, 'g': 0.3, 'b': 0.3}, width=1.0)
        graph.add_edge(1, 3, color={'r': 1.0, 'g': 0.3, 'b': 0.3}, width=1.0)
    
    return graph


#create a 3d graph network with layout (cube, sphere, line) default to cube
@plot_generator
def network_graph(layout: modcat(options=["cube", "sphere", "line"]) = "cube"):
    graph = Graph3DPlot()
    
    if layout == "cube":
        # 8 nodes in cube corners
        positions = [
            (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1),
            (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)
        ]
        
        for i, (x, y, z) in enumerate(positions):
            graph.add_node(i, x*3, y*3, z*3, 
                         label=f"Corner {i}",
                         color={'r': x, 'g': y, 'b': z})
        
        # connect cube edges
        edges = [(0,1), (0,2), (0,3), (1,4), (1,5), (2,4), (2,6), 
                (3,5), (3,6), (4,7), (5,7), (6,7)]
        for src, tgt in edges:
            graph.add_edge(src, tgt)
            
    elif layout == "sphere":
        # nodes distributed on sphere surface
        import math
        for i in range(8):
            phi = math.acos(1 - 2*i/8)
            theta = math.pi * (1 + 5**0.5) * i
            
            x = math.sin(phi) * math.cos(theta) * 2
            y = math.sin(phi) * math.sin(theta) * 2  
            z = math.cos(phi) * 2
            
            graph.add_node(i, x, y, z, 
                         label=f"Sphere {i}",
                         color={'r': 0.8, 'g': 0.4, 'b': 0.9})
        
        # connect nearby nodes
        for i in range(8):
            graph.add_edge(i, (i+1) % 8)
            if i < 4:
                graph.add_edge(i, i+4)
                
    else:  # line layout
        for i in range(6):
            graph.add_node(i, i*1.5, 0, i*0.5, 
                         label=f"Line {i}",
                         color={'r': 0.2, 'g': 0.8, 'b': 0.2})
            if i > 0:
                graph.add_edge(i-1, i)
    
    return graph


async def main():
    print("Adding 3D Graph examples...")
    await add_plot(simple_graph(num_nodes=5))
    await add_plot(network_graph())
    print("3D Graph plots added.")

if __name__ == "__main__":
    main()