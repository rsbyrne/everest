###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
from types import SimpleNamespace as _SimpleNamespace

from .bythos import Bythos as _Bythos
from . import ptolemaic as _ptolemaic


class AltReturn(Exception):

    __slots__ = ('value',)

    def __init__(self, value, /):
        self.value = value
        


class Urgon(_Bythos):

    @property
    def __get_signature__(cls, /):
        return cls.__class_get_signature__

    @property
    def __signature__(cls, /):
        try:
            return cls.__dict__['_classsignature']
        except KeyError:
            sig = cls.__get_signature__()
            type.__setattr__(cls, '_classsignature', sig)
            return sig

    def __call__(cls, /, *args, **kwargs):
        try:
            params = cls.__parameterise__(*args, **kwargs)
        except AltReturn as exc:
            return exc.value
        if cls.cacheable:
            return cls._retrieve_(params)
        return cls._construct_(params)

    def altreturn(cls, value, /):
        raise AltReturn(value)


class _UrgonBase_(metaclass=Urgon):

    cacheable = False

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, cls.__signature__.return_annotation)

    @classmethod
    def __class_includes__(cls, arg, /):
        return issubclass(arg, cls.__signature__.return_annotation)

    @classmethod
    @_abc.abstractmethod
    def __class_get_signature__(cls, /):
        raise NotImplementedError

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        # cls.__signature__ = cls.__get_signature__()
        if cls.cacheable:
            cls._premade = _weakref.WeakValueDictionary()

    @classmethod
    @_abc.abstractmethod
    def _construct_(cls, params: tuple = (), /):
        raise NotImplementedError

    @classmethod
    def __construct__(cls, params: tuple = (), /):
        return cls._construct_(cls._post_parameterise_(params))

    _parameterise_ = _SimpleNamespace

    @classmethod
    def _post_parameterise_(cls, params, /):
        if isinstance(params, _SimpleNamespace):
            params = params.__dict__.values()
        return tuple(map(cls.convert, params))

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        return cls._post_parameterise_(cls._parameterise_(*args, **kwargs))

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
        return cls._retrieve_(cls._post_parameterise_(params))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if cls.cacheable:
            return cls.__construct__(arg)
        return cls.__retrieve__(arg)


###############################################################################
###############################################################################
