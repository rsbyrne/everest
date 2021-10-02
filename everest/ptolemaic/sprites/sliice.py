###############################################################################
''''''
###############################################################################


from . import _Param

from .sprite import Sprite as _Sprite


class Sliice(_Sprite):

    args: _Param.Args

    reqslots = ('typ',)

    @classmethod
    def parameterise(cls, arg, /, *args):
        if args:
            return super().parameterise(arg, *args)
        if not isinstance(arg, slice):
            raise TypeError
        return super().parameterise(arg.start, arg.stop, arg.step)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls(arg.start, arg.stop, arg.step)

    def __init__(self, /):
        super().__init__()
        self.slc = slice(*self.args)
        typs = set(map(type, args))
        if len(typs) == 1:
            self.typ = typs.pop()
        else:
            self.typ = None

    def _repr(self, /):
        return ', '.join(map(repr, self.args))


###############################################################################
###############################################################################
