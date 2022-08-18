###############################################################################
''''''
###############################################################################


import inspect as _inspect
from types import MappingProxyType as _MappingProxyType

from .wisp import Wisp as _Wisp



class PathError(AttributeError):

    ...


class PathGet(metaclass=_Wisp):

    paths: tuple
    fallback: ... = NotImplemented

    @classmethod
    def _parameterise_(cls, /, *paths, fallback=NotImplemented):
        params = super()._parameterise_()
        if not all(map(str.__instancecheck__, paths)):
            raise TypeError("Path lengths must be strings.", paths)
        params.paths = paths
        params.fallback = fallback
        return params

    def __directive_call__(self, body, name, /):
        return name, self(body.namespace, body.module.__dict__)

    def __call__(self, arg, loc=_MappingProxyType({}), /):
        for path in self.paths:
            obj = arg
            names = iter(path.removesuffix('.').split('.'))
            name = next(names)
            if name:
                try:
                    obj = loc[name]
                except KeyError:
                    try:
                        obj = getattr(_inspect.getmodule(obj), name)
                    except AttributeError:
                        continue
            for name in names:
                if name:
                    try:
                        obj = getattr(obj, name)
                    except AttributeError:
                        break
                else:
                    obj = obj.__corpus__
            else:
                return _Wisp.convert(obj)
        else:
            if (fallback := self.fallback) is NotImplemented:
                raise PathError("Path retrieval failed!", obj, self)
            return fallback


###############################################################################
###############################################################################
