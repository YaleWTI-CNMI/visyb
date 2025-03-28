from typing import Type, Annotated, get_type_hints, Protocol, Callable,runtime_checkable

import inspect
import functools

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

class BuilderPlot:
    def __init__(self, xlim, ylim, zlim, **kwargs):
        self.type = "builder"
        self.objects = dict()

        self.xlim = xlim
        self.ylim = ylim
        self.zlim = zlim

        self.__dict__.update(kwargs)
        pass

    def add_line(self, x, y, z, color, id=None):
        if id is None:
            if len(self.objects) == 0:
                id = 0
            else:
                id = max(self.objects.keys()) + 1

        self.objects[id] = {
            "type": "line",
            "x": x,
            "y": y,
            "z": z,
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