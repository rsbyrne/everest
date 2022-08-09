###############################################################################
''''''
###############################################################################


import inspect as _inspect

from .sprite import Sprite as _Sprite


class Get(metaclass=_Sprite):

    path: str

    def __call__(self, obj, /):
        names = iter(self.path.removesuffix('.').split('.'))
        name = next(names)
        if name:
            obj = getattr(_inspect.getmodule(obj), name)
        for name in names:
            if name:
                obj = getattr(obj, name)
            else:
                obj = obj.__corpus__
        return obj



###############################################################################
###############################################################################
