###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from . import _utilities
from .pleroma import Pleroma as _Pleroma
from .sprite import Sprite as _Sprite, BadParameter as _BadParameter
from .primitive import Primitive as _Primitive
from . import shades as _shades

from . import exceptions as _exceptions


class BadParameter(_BadParameter):
    '''Raised when an unrecognised parameter type is detected.'''

    def message(self, /):
        yield from super().message()
        yield "or other Ptolemaics, or seen to be convertible to such"


# class Var(_Ptolemaic):
#     ...


class Dat(_shades.Singleton):

    isdat = True

    superclass = None

    @classmethod
    def _cls_repr(cls, /):
        return f"{repr(cls.superclass)}.{super()._cls_repr()}"


class Schema(_Sprite):

    _BadParameter = BadParameter

    _pleroma_fixedsubclasses__ = ('Mapp', 'Brace', 'Slyce')

    Mapp = _shades.DictLike
    Brace = _shades.TupleLike
    Slyce = _shades.SliceLike

    _pleroma_subclasses__ = ('Dat',)

    Dat = Dat

    isdat = False

    @classmethod
    def check_param(cls, arg, /):
        if isinstance(type(arg), _Pleroma):
            return arg
        try:
            return super().check_param(arg)
        except cls._BadParameter:
            try:
                meth = cls.checktypes[type(arg)]
            except KeyError as exc:
                raise cls._BadParameter(arg) from exc
            else:
                return meth(arg)

    @classmethod
    def yield_checktypes(cls, /):
        yield _Pleroma, lambda x: x
        yield _collabc.Mapping, lambda x: cls.Mapp(x)
        yield _collabc.Sequence, lambda x: cls.Brace(x)
        yield slice, lambda x: cls.Slyce(x)

    @classmethod
    def _cls_extra_init_(cls, /):
        cls.checktypes = _utilities.TypeMap(cls.yield_checktypes())

    @classmethod
    def prekey(cls, params):
        return params.hashID

    @classmethod
    def instantiate(cls, params, /, *args, **kwargs):
        if all(
                isinstance(param, (Dat, _Primitive, tuple, dict))
                for param in params.values()
                ):
            return cls.Dat.instantiate(params, *args, **kwargs)
        return super().instantiate(params, *args, **kwargs)

    def _repr(self):
        return self.params.hashID

    @property
    def hashID(self):
        return self._repr()


###############################################################################
###############################################################################
