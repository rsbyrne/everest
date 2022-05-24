###############################################################################
''''''
###############################################################################


import weakref as _weakref
from collections import abc as _collabc, namedtuple as _namedtuple
import functools as _functools
import inspect as _inspect

from everest import ur as _ur
from everest.utilities import pretty as _pretty

from .ousia import Ousia as _Ousia
from . import exceptions as _exceptions


class _Params_:

    def __new__(cls, /, *args, **kwargs):
        tup = super().__new__(cls, *args, **kwargs)
        return super().__new__(cls, *_ur.DatTuple(tup))

    @property
    def items(self, /):
        return self._asdict().items


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


class Composite(_Ousia):
    ...


class CompositeBase(metaclass=Composite):

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

    def remake(self, /, **kwargs):
        return self.__ptolemaic_class__.instantiate(
            tuple({**self.params._asdict(), **kwargs}.values())
            )

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    def initialise(self, params, /):
        object.__setattr__(self, 'params', params)
        super().initialise(params)

    @classmethod
    def instantiate(cls, params: _collabc.Sequence, /):
        params = cls.Params(*params)
        premade = cls.premade
        try:
            return premade[params]
        except KeyError:
            return super().instantiate(params)

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if cls.arity == 1:
            arg = (arg,)
        return cls.instantiate(arg)

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}" for key, val in self.params.items()
            )

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty_kwargs(self.params._asdict(), p, cycle, root=root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        params = self.params
        if ptolcls.arity == 1:
            params = params[0]
        return ptolcls.taphonomy.getitem_epitaph(ptolcls, params)


###############################################################################
###############################################################################
