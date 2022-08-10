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
        if isinstance(other, type):
            return True
        typ = type(other)
        if issubclass(typ, cls):
            return True
        # if typ is type:
        #     if other in _Primitive.TYPS:
        #         return True
        #     if other in _BUILTINS:
        #         return True
        #     return False
        if issubclass(typ, _types.ModuleType):
            return cls.check_module(typ)
        if issubclass(typ, _types.MethodType):
            return cls.__instancecheck__(other.__self__)
        if issubclass(typ, (_types.FunctionType, property)):
            return hasattr(other, '__corpus__')
        if issubclass(typ, property):
            return all(map(
                cls.__instancecheck__,
                (other.fget, other.fset, other.fdel),
                ))
        if issubclass(typ, _functools.partial):
            if not cls.__instancecheck__(other.func):
                return False
            params = _itertools.chain(other.args, other.keywords.values())
            return all(map(cls.__instancecheck__, params))
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
        # for nm in func.__qualname__.split('.')[:-1]:
        #     obj = getattr(obj, nm)
        #     if not cls.__instancecheck__(obj):
        #         return False
        return True

    @classmethod
    def check_module(cls, module, /):
        return True

#     @classmethod
#     @_functools.lru_cache()
#     def convert_type(cls, typ: type, /):
#         if issubclass(typ, Ptolemaic):
#             return typ
#         if issubclass(typ, set):
#             return PtolSet
#         if issubclass(typ, _np.ndarray):
#             return PtolArray
#         if issubclass(typ, _collabc.Mapping):
#             return PtolDict
#         if issubclass(typ, _collabc.Iterable):
#             return PtolTuple
#         raise TypeError(typ)

#     @classmethod
#     def convert(cls, obj, /):
#         if isinstance(obj, Ptolemaic):
#             return obj
#         if isinstance(obj, type):
#             return cls.convert_type(obj)
#         return cls.convert_type(type(obj))(obj)


for typ in Ptolemaic.TYPS:
    Ptolemaic.register(typ)
del typ


# convert_type = Ptolemaic.convert_type
# convert = Ptolemaic.convert


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


# @_ur.DatTuple.register
# class PtolTuple(_ur.TupleBase, Ptolemaic):

#     __slots__ = ()


# @_ur.DatUniTuple.register
# class PtolUniTuple(_ur.UniTupleBase, Ptolemaic):

#     __slots__ = ()


# @_ur.DatSet.register
# class PtolSet(_ur.SetBase, Ptolemaic):

#     __slots__ = ()


# @_ur.DatDict.register
# class PtolDict(_ur.DictBase, Ptolemaic):

#     __slots__ = ()


# @_ur.DatArray.register
# class PtolArray(_ur.ArrayBase, Ptolemaic):

#     __slots__ = ()


def get_innerobj_taphonomiser(owner, name, /):
    def _make_epitaph_(taph, /):
        return taph.getattr_epitaph(owner, name)
    return _make_epitaph_


def configure_as_innerobj(obj, owner, name, /):
    if isinstance(obj, Ideal):
        assert obj.__mutable__
        obj.__class_relname__ = name
        obj.__class_corpus__ = owner
        if isinstance(owner, Ideal):
            obj.__qualname__ = owner.__qualname__ + '.' + name
    elif isinstance(obj, Case):
        assert obj.__mutable__
        obj.__corpus__, obj.__relname__ = owner, name
    else:
        if hasattr(obj, '__corpus__'):
            raise RuntimeError("Object is already an inner object!")
        obj.__corpus__, obj.__relname__ = owner, name
        obj.__taphonomise__ = get_innerobj_taphonomiser(owner, name)


def get_calling_scope_name(name: str, /):
    frame = _inspect.stack()[1][0]
    while name not in frame.f_locals:
        frame = frame.f_back
        if frame is None:
            return None
    return frame.f_locals[name]


###############################################################################
###############################################################################
