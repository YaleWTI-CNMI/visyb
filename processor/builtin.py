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
        self.__dict__.update(kwargs)

    pass

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
        self.mods[name].value = newval

    def to_client_dict(self):
        return {"id": self.id, "mods": self.mods, "result": self.result}

def to_client_dict(obj):
    if hasattr(obj, 'to_client_dict') and callable(obj.to_client_dict):
        return to_client_dict(obj.to_client_dict())
    elif isinstance(obj, dict):
        return {
            to_client_dict(k): to_client_dict(v)
            for k, v in obj.items()
        }
    elif isinstance(obj, (list, tuple, set)):
        print(f'----- {obj}')
        return type(obj)(to_client_dict(item) for item in obj)
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        if hasattr(obj, '__dict__'):
            return to_client_dict(vars(obj))
        else:
            return str(obj)

def plot_generator(func: Callable):
    mods = {}
    for _, param in inspect.signature(func).parameters.items():
        try:
            mod = param.annotation.__metadata__[0]
            if isinstance(mod, Modifier):
                mods[param.name] = {"definition": mod, "value": param.default}
        except:
            continue

    print(mods)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return PlotGenerator(func, args, kwargs, mods)

    return wrapper