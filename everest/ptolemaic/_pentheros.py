###############################################################################
''''''
###############################################################################


from inspect import Signature as _Signature, Parameter as _Parameter, _empty
import types as _types

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


class ProvisionalParams(_types.SimpleNamespace):

    def __iter__(self, /):
        return iter(self.__dict__.values())


class PentherosBase(metaclass=Pentheros):

    @classmethod
    def _get_sig(cls, /):
        return _Sig(cls)

    @classmethod
    def __class_init__(cls, /):
        cls.__field_names__ = tuple(cls.sig.keys())
        super().__class_init__()

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return ProvisionalParams(**bound.arguments)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(tuple(cls.parameterise(*args, **kwargs)))


###############################################################################
###############################################################################
