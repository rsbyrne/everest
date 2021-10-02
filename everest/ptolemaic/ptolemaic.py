###############################################################################
''''''
###############################################################################


import itertools as _itertools

from . import _utilities

from .pleroma import Pleromatic as _Pleromatic
from .primitive import Primitive as _Primitive

from . import exceptions as _exceptions


class BadParameter(_exceptions.ParameterisationException):
    '''Raised when an unrecognised parameter type is detected.'''

    __slots__ = ('param',)

    def __init__(self, param, /):
        self.param = param

    def message(self, /):
        yield from super().message()
        yield "when an object of unrecognised type was passed as a parameter."
        try:
            rep = repr(self.param)
        except Exception as exc:
            yield 'While writing this message, another exception occurred:'
            yield str(exc)
        else:
            yield 'The object looked something like this:'
            yield rep


class PtolemaicBase(_Pleromatic):
    '''
    The base class of all object types
    understood as inputs for the Ptolemaic system.
    '''


_ = PtolemaicBase.register(_Primitive)


class Ptolemaic(PtolemaicBase):

    BadParameter = BadParameter

    @classmethod
    def yield_checktypes(cls, /):
        return
        yield

    @classmethod
    def _cls_extra_init_(cls, /):
        super()._cls_extra_init_()
        cls.checktypes = _utilities.TypeMap(cls.yield_checktypes())

    def __init__(self, /):
        pass

    def _repr(self, /):
        return self.params.__str__()

    @_utilities.caching.soft_cache(None)
    def __repr__(self, /):
        return f"{type(self).basecls.__qualname__}({self._repr()})"

    @classmethod
    def check_param(cls, arg, /):
        if not isinstance(arg, PtolemaicBase):
            try:
                meth = cls.checktypes[type(arg)]
            except KeyError as exc:
                raise BadParameter(arg) from exc
            else:
                arg = meth(arg)
        return super().check_param(arg)


###############################################################################
###############################################################################
