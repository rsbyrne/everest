###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import types as _types
import inspect as _inspect

from .essence import Essence as _Essence
from . import ptolemaic as _ptolemaic


class Urgon(_Essence):

    ...


class _UrgonBase_(metaclass=Urgon):

    @classmethod
    def _get_signature(cls, /):
        try:
            func = cls.__class_call__
        except AttributeError:
            func = lambda: None
        return _inspect.signature(func)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__signature__ = cls._get_signature()
        cls._premade = _weakref.WeakValueDictionary()

    @classmethod
    @_abc.abstractmethod
    def _construct_(cls, params: tuple = (), /):
        raise NotImplementedError

    @classmethod
    def __construct__(cls, params: tuple = (), /):
        return cls._construct_(_ptolemaic.convert(params))

    __parameterise__ = _types.SimpleNamespace

    @classmethod
    def _retrieve_(cls, params: tuple, /):
        premade = cls._premade
        try:
            return premade[params]
        except KeyError:
            obj = premade[params] = cls._construct_(params)
            return obj

    @classmethod
    def __retrieve__(cls, params: tuple, /):
        return cls._retrieve_(_ptolemaic.convert(params))

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.__retrieve__(tuple(
            cls.__parameterise__(*args, **kwargs)
            .__dict__.values()
            ))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        return cls.__retrieve__(arg)


###############################################################################
###############################################################################
