###############################################################################
''''''
###############################################################################


from . import _utilities
from .pleroma import Pleroma as _Pleroma
from .sprite import Sprite as _Sprite, BadParameter as _BadParameter


class BadParameter(_BadParameter):
    '''Raised when an unrecognised parameter type is detected.'''

    def message(self, /):
        yield from super().message()
        yield "or other Ptolemaics, or seen to be convertible to such"


class Ptolemaic(_Sprite):

    _BadParameter = BadParameter

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

    @classmethod
    def _cls_extra_init_(cls, /):
        cls.checktypes = _utilities.TypeMap(cls.yield_checktypes())

    @classmethod
    def prekey(cls, params):
        return params.hashID

    def _repr(self):
        return self.params.hashID

    @property
    def hashID(self):
        return self._repr()


###############################################################################
###############################################################################
