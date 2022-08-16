###############################################################################
''''''
###############################################################################


import inspect as _inspect

from .wisp import Wisp as _Wisp



class PathError(RuntimeError):

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
        val = body.get_from_path(*self.paths, fallback=self.fallback)
        return name, val

    def __call__(self, obj, /):
        for path in self.paths:
            names = iter(path.removesuffix('.').split('.'))
            name = next(names)
            if name:
                try:
                    obj = getattr(_inspect.getmodule(obj), name)
                except AttributError:
                    continue
            for name in names:
                if name:
                    try:
                        obj = getattr(obj, name)
                    except AttributeError:
                        continue
                else:
                    obj = obj.__corpus__
            return _Wisp.convert(obj)
        else:
            if (fallback := self.fallback) is NotImplemented:
                raise AttributeError(obj, self)
            return fallback


###############################################################################
###############################################################################
