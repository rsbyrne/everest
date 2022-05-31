###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
from collections import abc as _collabc, namedtuple as _namedtuple
import functools as _functools
import inspect as _inspect

from everest import ur as _ur

from .essence import Essence as _Essence
from . import exceptions as _exceptions


class _Params_:

    def __new__(cls, /, *args, **kwargs):
        tup = super().__new__(cls, *args, **kwargs)
        return super().__new__(cls, *_ur.DatTuple(tup))

    @property
    def items(self, /):
        return self._asdict().items

    @property
    def values(self, /):
        return self._asdict().values

    @property
    def keys(self, /):
        return self._asdict().keys


@_functools.wraps(_namedtuple)
def paramstuple(*args, **kwargs):
    nt = _namedtuple(*args, **kwargs)
    out = type(f"Params_{nt.__name__}", (_Params_, nt), {})
    out.__signature__ = _inspect.signature(nt)
    return out


class ProvisionalParams(dict):

    def __setitem__(self, name, val, /):
        if name not in self:
            raise KeyError(name)
        super().__setitem__(name, val)

    @property
    def __delitem__(self, /):
        raise AttributeError

    def __getattr__(self, name, /):
        return self[name]

    def __setattr__(self, name, val, /):
        return self.__setitem__(name, val)

    def __iter__(self, /):
        return iter(self.values())

    @property
    def _fields(self, /):
        return tuple(self.values())


class Pentheros(_Essence):

    @_abc.abstractmethod
    def construct(cls, /, *_, **__):
        raise NotImplementedError

    @property
    def arity(cls, /):
        return len(cls.Params._fields)


class PentherosBase(metaclass=Pentheros):

    @classmethod
    def _make_params_type(cls, /) -> type:
        return paramstuple(cls.__name__, ())

    @classmethod
    def _get_signature(cls, /):
        return _inspect.signature(cls.Params)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.premade = _weakref.WeakValueDictionary()
        cls.Params = cls._make_params_type()

    @classmethod
    def parameterise(cls, /, *args, **kwargs) -> _collabc.Mapping:
        return ProvisionalParams(cls.Params(*args, **kwargs)._asdict())

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    @classmethod
    def retrieve(cls, params: _collabc.Sequence, /):
        params = cls.Params(*params)
        premade = cls.premade
        try:
            return premade[params]
        except KeyError:
            out = premade[params] = cls.construct(params)
            return out

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.retrieve(cls.parameterise(*args, **kwargs))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if cls.arity == 1:
            arg = (arg,)
        return cls.retrieve(arg)

    @classmethod
    def construct_epitaph(cls, params, /):
        params = params[0] if cls.arity == 1 else tuple(params)
        return cls.taphonomy.getitem_epitaph(cls, params)


###############################################################################
###############################################################################
