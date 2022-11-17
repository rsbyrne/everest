###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import inspect as _inspect
from types import SimpleNamespace as _SimpleNamespace

from .wisp import Namespace as _Namespace, Partial as _Partial
from .bythos import Bythos as _Bythos
from . import ptolemaic as _ptolemaic


class Params(_Namespace):

    ...


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
        return (
            (cls._retrieve_ if cls.cacheable else cls._construct_)
            (cls._parameterise_(*args, **kwargs))
            )


class _UrgonBase_(metaclass=Urgon):

    cacheable = False

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, cls.__signature__.return_annotation)

    @classmethod
    def __class_includes__(cls, arg, /):
        return issubclass(arg, cls.__signature__.return_annotation)

    @classmethod
    def __class_get_signature__(cls, /):
        return _inspect.Signature()

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        # cls.__signature__ = cls.__get_signature__()
        if cls.cacheable:
            cls._premade = _weakref.WeakValueDictionary()

    @classmethod
    @_abc.abstractmethod
    def _construct_(cls, params, /):
        raise NotImplementedError

    _parameterise_ = _SimpleNamespace

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return Params(cls._parameterise_(*args, **kwargs))

    @classmethod
    def partial(cls, /, *args, **kwargs):
        return _Partial(cls, *args, **kwargs)

    @classmethod
    def _retrieve_(cls, params: Params, /):
        params = Params(params)
        premade = cls._premade
        try:
            return premade[params]
        except KeyError:
            obj = premade[params] = cls._construct_(params)
            return obj

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if cls.cacheable:
            return cls._construct_(arg)
        return cls._retrieve_(arg)


###############################################################################
###############################################################################
