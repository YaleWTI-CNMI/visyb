import itertools
from dataclasses import dataclass, field
import weakref
from functools import partial


###########################################
__vrid_counter__ = itertools.count(start=1)
__vrid_registry__ = weakref.WeakValueDictionary()
############################################


def VRID(obj) -> int:
    if obj is None:
        raise RuntimeError("No object provided while generating VRID")

    vrid = next(__vrid_counter__)
    __vrid_registry__[vrid] = obj
    return vrid


def get_vrid_handler(vrid) -> callable:
    obj = __vrid_registry__.get(vrid)
    if obj is None:
        return None

    handler = getattr(obj, "vrid_handler", None)
    if callable(handler):
        return handler

    return None


@dataclass
class HasVRID:
    vrid: int = field(init=False)

    def __post_init__(self):
        self.vrid = VRID(self)