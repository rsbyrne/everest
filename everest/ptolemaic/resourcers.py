###############################################################################
''''''
###############################################################################


from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
from functools import partial as _partial, reduce as _reduce
import types as _types
import itertools as _itertools

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.aspect import (
    Aspect as _Aspect, Functional as _Functional
    )
from everest.ptolemaic.proxy import Proxy as _Proxy
from everest.ptolemaic.sprite import Sprite as _Sprite


class _ResourcerBase_(_Aspect):

    CONVERTTYPES = ()

    @classmethod
    def can_convert(cls, arg, /) -> bool:
        for typ in cls.CONVERTTYPES:
            if isinstance(arg, typ):
                return True
        return False


class _ResourcerProper_(_Proxy, _ResourcerBase_, _Sprite):

    _req_slots__ = ('makefn', '_call_')

    def __init__(self, makefn, /):
        self.makefn = makefn
        self.reset()

    def reset(self, ref=None, /):
        self._call_ = self._original_call__

    def _original_call__(self, /):
        out = self.makefn()
        self._call_ = _ref(out, self.reset)
        return out

    @property
    def __call__(self, /):
        return self._call_

    def unproxy(self, /):
        return self()


class Module(_ResourcerProper_):

    CONVERTTYPES = (_types.ModuleType,)

    @classmethod
    def parameterise(self, register, arg, /):
        if isinstance(arg, _types.module):
            arg = arg.__name__
        register(arg)

    def __init__(self, path, /):
        super().__init__(
            _partial(_import_module, path)
            )


class Content(_ResourcerProper_):

    CONVERTTYPES = (
        type,
        _types.FunctionType,
        _types.MethodType,
        _types.BuiltinFunctionType,
        _types.BuiltinMethodType,
        )

    @classmethod
    def parameterise(self, register, arg0, arg1=None, /):
        if arg1 is None:
            arg0, arg1 = arg0.__qualname__, _getmodule(arg0).__name__
        register(arg0, arg1)

    def __init__(self, name, path, /):
        super().__init__(
            lambda: _reduce(getattr, name.split('.'), _import_module(path))
            )


class PtolContent(_ResourcerBase_, _Functional):

    CONVERTTYPES = (
        _Essence,
        )

    @classmethod
    def method(cls, arg, /):
        out = arg.classproxy
        if isinstance(out, type):
            return Content(out)
        return out


class Resourcer(_Functional, _ResourcerBase_):

    CONVERTERS = (Module, PtolContent, Content)
    CONVERTTYPES = tuple(_itertools.chain.from_iterable(
        typ.CONVERTTYPES for typ in CONVERTERS
        ))

    for i, typ in enumerate(CONVERTERS):
        exec(f"{typ.__name__} = CONVERTERS[{i}]")

    @classmethod
    def method(cls, arg, /):
        for typ in cls.CONVERTERS:
            if typ.can_convert(arg):
                return typ(arg)
        raise TypeError(type(arg))

# class Demiurge(/


###############################################################################
###############################################################################
