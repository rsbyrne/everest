###############################################################################
''''''
###############################################################################


import itertools as _itertools

from . import _utilities

from .shade import Shade as _Shade
from .primitive import Primitive as _Primitive

from . import exceptions as _exceptions


class BadParameter(_exceptions.ParameterisationException):

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
        yield ''.join((
            "Note that this class only accepts inputs which are Primitives",
            " (e.g. Python int, float, bool)"
            ))


class Sprite(_Shade):

    _BadParameter = BadParameter

    @classmethod
    def check_param(cls, arg, /):
        if isinstance(arg, _Primitive):
            return arg
        raise cls._BadParameter(arg)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return type(cls).parameterise(cls,
            *map(cls.check_param, args),
            **dict(zip(kwargs, map(cls.check_param, kwargs.values()))),
            )

    @classmethod
    def instantiate(cls, params, /):
        return type(cls).instantiate(cls, params)

    @classmethod
    def construct(cls, /, *args, **kwargs):
        return type(cls).construct(cls, *args, **kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return type(cls).__class_getitem__(cls, arg)

    def __init__(self, /):
        pass

    def _repr(self, /):
        return self.params.__str__()

    @classmethod
    def _cls_repr(cls, /):
        if cls._pleroma_concrete__:
            cls = cls.basecls
        return cls.__qualname__

    @_utilities.caching.soft_cache()
    def __repr__(self, /):
        return f"{self._cls_repr()}({self._repr()})"


###############################################################################
###############################################################################
