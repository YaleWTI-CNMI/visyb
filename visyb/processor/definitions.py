from typing import Type, Annotated, get_type_hints, Protocol, Callable,runtime_checkable

import inspect
import functools
import copy

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
            if obj_vrid == vrid and callable(data.get("onclick")):
                data["onclick"](index)
        return

    def add_point_set(self, x, y, z, color={"r": 1, "g": 1, "b": 1}, size=0.01, onclick=None, metadata=[]):
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
            "onclick": onclick,
            "metadata": metadata,
            "size": size
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
        self.mods = copy.deepcopy(mods)
        self.id = -1
        initial = inspect.signature(self.func).bind_partial(*self.args, **self.kwargs)
        for name, mod in self.mods.items():
            if name in initial.arguments:
                mod["value"] = initial.arguments[name]

        self.run()

    def run(self):
        bound = inspect.signature(self.func).bind_partial(*self.args, **self.kwargs)
        bound.arguments.update({name: mod["value"] for name, mod in self.mods.items()})
        self.result = self.func(*bound.args, **bound.kwargs)

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
