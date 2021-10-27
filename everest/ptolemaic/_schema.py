###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from .system import System as _System

from .primitive import Primitive as _Primitive
from . import shades as _shades
# from .shade import Shade as _Shade


# class Var(_Ptolemaic):
#     ...


class Dat(_shades.Singleton):
# class Dat(_Shade):

    isdat = True

    superclass = None

    @classmethod
    def _cls_repr(cls, /):
        return f"{repr(cls.superclass)}.{super()._cls_repr()}"


class Schema(_System):

    _ptolemaic_fixedsubclasses__ = ('Mapp', 'Brace', 'Slyce')

    Mapp = _shades.DictLike
    Brace = _shades.TupleLike
    Slyce = _shades.SliceLike

    _ptolemaic_subclasses__ = ('Dat',)

    Dat = Dat

    isdat = False

    @classmethod
    def yield_checktypes(cls, /):
        yield from super().yield_checktypes()
        yield _collabc.Mapping, lambda x: cls.Mapp(x)
        yield _collabc.Sequence, lambda x: cls.Brace(x)
        yield slice, lambda x: cls.Slyce(x)

    @classmethod
    def instantiate(cls, params, /, *args, **kwargs):
        if all(
                isinstance(param, (Dat, _Primitive, tuple, dict))
                for param in params.values()
                ):
            return cls.Dat.instantiate(params, *args, **kwargs)
        return super().instantiate(params, *args, **kwargs)


###############################################################################
###############################################################################