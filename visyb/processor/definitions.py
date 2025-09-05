from typing import Type, Annotated, get_type_hints, Protocol, Callable,runtime_checkable

import inspect
import functools

from visyb.utils import vrid

@runtime_checkable
class Modifier(Protocol):
    def basetype() -> Type: ...

    def validate(self, value) -> bool: ...

    def to_type_hint(self) -> Type:
        return Annotated[
            self.__class__.basetype(),
            self
        ]

    def to_client_dict(self):
        return self.__dict__


class ContinuousModifier(Modifier):
    def __init__(self, range=[None, None], step=1):
        self.type = "continuous"
        self.range = range
        self.step = step

    def basetype() -> Type:
        return float

    def validate(self, value) -> bool:
        if not isinstance(value, float):
            return False

        if self.range[0] is not None and value < self.range[0]:
            return False

        if self.range[1] is not None and value > self.range[1]:
            return False

        return True

class CategoricalModifier(Modifier):
    def __init__(self, options=[]):
        self.type = "categorical"
        self.options = options

    def basetype():
        return str

    def validate(self, value) -> bool:
        return value in self.options

class BoolModifier(Modifier):
    def __init__(self):
        pass

    def basetype():
        return bool

    def validate(self, value) -> bool:
        return value in self.options

def modcont(*args, **kwargs):
    mod = ContinuousModifier(*args, **kwargs)
    return mod.to_type_hint()

def modcat(*args, **kwargs):
    mod = CategoricalModifier(*args, **kwargs)
    return mod.to_type_hint()

def modbool(*args, **kwargs):
    mod = BoolModifier(*args, **kwargs)
    return mod.to_type_hint()

class ScatterPlot:
    def __init__(self, **kwargs):
        self.type = "scatter"
        self.xlim = [min(*kwargs["x"]), max(*kwargs["x"])]
        self.ylim = [min(*kwargs["y"]), max(*kwargs["y"])]
        self.zlim = [min(*kwargs["z"]), max(*kwargs["z"])]

        self.__dict__.update(kwargs)

    pass

class Model3DPlot:
    def __init__(self, data, format, **kwargs):
        self.type = "model3d"
        self.data = data
        self.format = format
        self.__dict__.update(kwargs)

class BuilderPlot:
    def __init__(self, xlim, ylim, zlim, **kwargs):
        self.type = "builder"
        self.objects = dict()

        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim

        self.__dict__.update(kwargs)
        pass


    def vrid_handler(self, vrid, action, index):
        for obj_vrid, data in self.objects.items():
            if obj_vrid == vrid and "onclick" in data:
                data["onclick"](index)
        return

    def add_point_set(self, x, y, z, color={"r": 1, "g": 1, "b": 1}, onclick=None):
        obj_vrid = vrid.VRID(self)
        self.objects[obj_vrid] = {
            "type": "point_set",
            "vrid": obj_vrid,
            "x": x,
            "y": y,
            "z": z,
            "xlim": self.xlim,
            "ylim": self.ylim,
            "zlim": self.zlim,
            "color": color,
            "onclick": onclick
        }

        return

    def add_line(self, x, y, z, color):
        obj_vrid = vrid.VRID(self)
        self.objects[obj_vrid] = {
            "type": "line",
            "vrid": obj_vrid,
            "x": x,
            "y": y,
            "z": z,
            "xlim": self.xlim,
            "ylim": self.ylim,
            "zlim": self.zlim,
            "color": color
        }



class PlotGenerator:
    def __init__(self, func, args, kwargs, mods):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.mods = mods
        self.id = -1

        self.run()

    def run(self):
        self.result = self.func(
            *self.args,
            **self.kwargs,
            **{k: v["value"] for k, v in self.mods.items()})

    def update_mod(self, name, newval):
        self.mods[name]["value"] = newval
        self.run()

    def to_client_dict(self):
        return {"id": self.id, "mods": self.mods, "result": self.result}


def plot_generator(func: Callable):
    mods = {}
    for _, param in inspect.signature(func).parameters.items():
        try:
            mod = param.annotation.__metadata__[0]
            if isinstance(mod, Modifier):
                mods[param.name] = {"definition": mod, "value": param.default}
        except:
            continue

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return PlotGenerator(func, args, kwargs, mods)

    return wrapper


#  3D Graph visualization with interactive nodes

class Graph3DPlot:

    def __init__(self, movable_nodes=False):
        self.movable_nodes = movable_nodes
        self.nodes = []
        self.edges = []
        self.id = None
        self.node_callbacks = {}

    def add_node(self, id, x, y, z, label=None, color=None, size=1.0, movable=None, on_move=None, **kwargs):
        # add a node to the graph
        node = {
            'id': id,
            'x': x,
            'y': y,
            'z': z,
            'label': label or str(id),
            'color': color or {'r': 0.5, 'g': 0.5, 'b': 1.0},
            'size': size,
            'movable': movable if movable is not None else self.movable_nodes,
            **kwargs
        }

        # store callback if provided
        if on_move is not None:
            self.node_callbacks[id] = on_move

        self.nodes.append(node)

    def add_edge(self, source_id, target_id, color=None, width=1.0, **kwargs):
        # add edge between nodes
        edge = {
            'source_id': source_id,
            'target_id': target_id,
            'color': color or {'r': 0.8, 'g': 0.8, 'b': 0.8},
            'width': width,
            **kwargs
        }
        self.edges.append(edge)

    def get_node_by_id(self, node_id):
        # get node by id
        for node in self.nodes:
            if str(node['id']) == str(node_id):
                return node
        return None

    def update_node_position(self, node_id, x, y, z):
        # update node position and trigger callback if any
        node = self.get_node_by_id(node_id)
        if node:
            node['x'] = x
            node['y'] = y
            node['z'] = z

            # trigger callback if any
            if node_id in self.node_callbacks:
                try:
                    self.node_callbacks[node_id](node_id, x, y, z)
                except Exception as e:
                    print(f"Error calling callback for node with id{node_id}: {e}")

            return True
        return False

    def to_client_dict(self):
        # convert to dictionary
        return {
            'id': self.id,
            'type': 'graph3d',
            'nodes': self.nodes,
            'edges': self.edges,
            'movable_nodes': self.movable_nodes
        }