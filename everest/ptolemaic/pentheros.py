###############################################################################
''''''
###############################################################################


from inspect import Signature as _Signature, Parameter as _Parameter, _empty
import weakref as _weakref

from everest.utilities import caching as _caching

from .composite import Composite as _Composite
from .sig import Sig as _Sig
from . import exceptions as _exceptions


class Pentheros(_Composite):

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    @property
    def fields(cls, /):
        return cls.sig.sigfields


class PentherosBase(metaclass=Pentheros):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.sig = cls._get_sig()

    @classmethod
    def _get_sig(cls, /):
        return _Sig(cls)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__field_slots__ = tuple(cls.sig.keys())
        cls.premade = _weakref.WeakValueDictionary()

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @classmethod
    def instantiate(cls, fieldvals: tuple, /):
        try:
            return cls.premade[fieldvals]
        except KeyError:
            obj = cls.premade[fieldvals] = super().instantiate(fieldvals)
            return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(tuple(
            cls.parameterise(*args, **kwargs).arguments.values()
            ))


###############################################################################
###############################################################################
