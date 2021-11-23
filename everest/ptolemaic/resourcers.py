###############################################################################
''''''
###############################################################################


from importlib import import_module as _import_module
from inspect import getmodule as _getmodule
from functools import partial as _partial, reduce as _reduce
import types as _types
import itertools as _itertools

from everest.utilities.constructor import Constructor as _Constructor
from everest.ptolemaic.aspect import Aspect as _Aspect
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


class _ResourcerProper_(_Proxy, _ResourcerBase_, _Sprite, _Constructor):

    def unproxy(self, /):
        return self()


class Module(_ResourcerProper_):

    CONVERTTYPES = (_types.ModuleType,)

    @classmethod
    def parameterise(self, register, arg, /):
        if isinstance(arg, _types.module):
            arg = arg.__name__
        super().parameterise(register, arg)

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
        super().parameterise(register, arg0, arg1)

    def __init__(self, name, path, /):
        super().__init__(
            lambda: _reduce(getattr, name.split('.'), _import_module(path))
            )


class Resourcer(_ResourcerBase_):

    CONVERTERS = (Module, Content)
    CONVERTTYPES = tuple(_itertools.chain.from_iterable(
        typ.CONVERTTYPES for typ in CONVERTERS
        ))

    for i, typ in enumerate(CONVERTERS):
        exec(f"{typ.__name__} = CONVERTERS[{i}]")

    @classmethod
    def construct(cls, arg, /):
        for typ in (Module, Content):
            if typ.can_convert(arg):
                return typ(arg)
        raise TypeError(type(arg))

    @classmethod
    def _ptolemaic_issubclass__(cls, arg, /):
        return issubclass(arg, _ResourcerBase_)

# class Demiurge(/


###############################################################################
###############################################################################
