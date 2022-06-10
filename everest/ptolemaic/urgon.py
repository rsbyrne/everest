###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import types as _types
import inspect as _inspect

from .essence import Essence as _Essence
from . import exceptions as _exceptions


class Urgon(_Essence):

    ...


class _UrgonBase_(metaclass=Urgon, _isbasetyp_=True):

    @classmethod
    def _get_signature(cls, /):
        try:
            func = cls.__class_call__
        except AttributeError:
            func = lambda: None
        return _inspect.signature(func)

    @classmethod
    def __class_deep_init__(cls, /):
        super().__class_deep_init__()
        cls.__signature__ = cls._get_signature()

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        premade = _weakref.WeakValueDictionary()
        cls._premade = premade
        cls.premade = _types.MappingProxyType(premade)

    @classmethod
    @_abc.abstractmethod
    def construct(cls, params, /):
        raise NotImplementedError

    parameterise = _types.SimpleNamespace

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    @classmethod
    def retrieve(cls, params: tuple, /):
        premade = cls._premade
        try:
            return premade[params]
        except KeyError:
            obj = premade[params] = cls.construct(params)
            return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.retrieve(tuple(
            cls.parameterise(*args, **kwargs)
            .__dict__.values()
            ))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, params, /):
        return cls.retrieve(params)


###############################################################################
###############################################################################
