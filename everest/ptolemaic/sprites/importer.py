###############################################################################
''''''
###############################################################################


from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
import functools as _functools

from everest.utilities.constructor import Constructor as _Constructor
from everest.ptolemaic.sprites.sprite import Sprite as _Sprite


class Importer(_Sprite, _Constructor):

    @classmethod
    def parameterise(self, register, arg0, arg1=None, /):
        if arg1 is None:
            arg0, arg1 = arg0.__qualname__, _getmodule(arg0).__name__
        super().parameterise(register, arg0, arg1)

    def __init__(self, name, path, /):
        super().__init__(_functools.partial(self.make_class, name, path))

    @staticmethod
    def make_class(name, path):
        obj = _import_module(path)
        for subname in name.split('.'):
            obj = getattr(obj, subname)
        return obj


# class Demiurge(/


###############################################################################
###############################################################################
