###############################################################################
''''''
###############################################################################


import functools as _functools
from collections import abc as _collabc
import types as _types
import inspect as _inspect
import itertools as _itertools
import builtins as _builtins

import numpy as _np

from everest import ur as _ur


_BUILTINS = _builtins.__dict__.values()

_Primitive = _ur.Primitive


_PSEUDOINSTANCES = tuple(map(id, _Primitive.TYPS))


class PtolemaicMeta(_ur.DatMeta):

    def __instancecheck__(cls, other, /):
        if cls is not Ptolemaic:
            return super().__instancecheck__(other)
        typ = type(other)
        if issubclass(typ, cls):
            return True
        if typ is type:
            if other in _Primitive.TYPS:
                return True
            if other in _BUILTINS:
                return True
            return False
        if issubclass(typ, _types.ModuleType):
            return cls.check_module
        if issubclass(typ, _types.MethodType):
            return cls.__instancecheck__(other.__self__)
        if issubclass(typ, _types.FunctionType):
            return cls.check_func(other)
        if issubclass(typ, _functools.partial):
            if not cls.__instancecheck__(other.func):
                return False
            params = _itertools.chain(other.args, other.keywords.values())
            return all(map(cls.__instancheck__, params))
        return super().__instancecheck__(other)


class Ptolemaic(_ur.Dat, metaclass=PtolemaicMeta):

    __slots__ = ()

    TYPS = (
        _types.BuiltinFunctionType,
        _types.BuiltinMethodType,
        _ur.PseudoType,
        )

    @classmethod
    def check_func(cls, func, /):
        obj = module = _inspect.getmodule(func)
        if not cls.check_module(module):
            return False
        for nm in func.__qualname__.split('.')[:-1]:
            obj = getattr(obj, nm)
            if not cls.__instancecheck__(obj):
                return False
        return True

    @classmethod
    def check_module(cls, module, /):
        return True

    @classmethod
    @_functools.lru_cache()
    def convert_type(cls, typ: type, /):
        if issubclass(typ, Ptolemaic):
            return typ
        if issubclass(typ, set):
            return PtolSet
        if issubclass(typ, _np.ndarray):
            return PtolArray
        if issubclass(typ, _collabc.Mapping):
            return PtolDict
        if issubclass(typ, _collabc.Iterable):
            return PtolTuple
        raise TypeError(typ)

    @classmethod
    def convert(cls, obj, /):
        if isinstance(obj, Ptolemaic):
            return obj
        if isinstance(obj, type):
            return cls.convert_type(obj)
        return cls.convert_type(type(obj))(obj)


for typ in Ptolemaic.TYPS:
    Ptolemaic.register(typ)
del typ


convert_type = Ptolemaic.convert_type
convert = Ptolemaic.convert


Ptolemaic.register(PtolemaicMeta)
Ptolemaic.register(_Primitive)


class Transcendant(PtolemaicMeta):

    def __call__(cls, /, *_, **__):
        raise NotImplementedError


@Ptolemaic.register
class Theme(metaclass=Transcendant):
    ...


@Ptolemaic.register
class Ideal(metaclass=Transcendant):
    ...


@Ptolemaic.register
class Kind(Ideal):
    ...


@Ptolemaic.register
class Case(metaclass=Transcendant):
    ...


@_ur.DatTuple.register
class PtolTuple(_ur.TupleBase, Ptolemaic):

    __slots__ = ()


@_ur.DatUniTuple.register
class PtolUniTuple(_ur.UniTupleBase, Ptolemaic):

    __slots__ = ()


@_ur.DatSet.register
class PtolSet(_ur.SetBase, Ptolemaic):

    __slots__ = ()


@_ur.DatDict.register
class PtolDict(_ur.DictBase, Ptolemaic):

    __slots__ = ()


@_ur.DatArray.register
class PtolArray(_ur.ArrayBase, Ptolemaic):

    __slots__ = ()


###############################################################################
###############################################################################
