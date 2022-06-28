###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import types as _types
from enum import Enum as _Enum
import functools as _functools

import numpy as _np

from everest.utilities import pretty as _pretty


class UrMeta(_abc.ABCMeta):
    ...


class Ur(metaclass=UrMeta):

    __slots__ = ()


class CollectionBase(metaclass=_abc.ABCMeta):

    __slots__ = ()

    def __init_subclass__(cls, /, **kwargs):
        super().__init_subclass__(**kwargs)
        if issubclass(cls, Ur):
            if not all(
                    hasattr(cls, attr)
                    for attr in ('convert', 'convert_type')
                    ):
                raise TypeError(cls)

    def __setattr__(self, name, val, /):
        raise AttributeError

    def __delattr__(self, name, /):
        raise AttributeError


class TupleBase(tuple, CollectionBase):

    __slots__ = ()

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, map(cls.convert, iterable))

    def __repr__(self, /):
        return type(self).__qualname__ + super().__repr__()

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_tuple(self, p, cycle, root=root)


class UniTupleBase(tuple, CollectionBase):

    __slots__ = ()

    @classmethod
    def _yield_unique(cls, iterable, /):
        seen = set()
        for item in iterable:
            if item not in seen:
                yield item
                seen.add(item)

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, cls._yield_unique(
            map(cls.convert, iterable)
            ))

    def __repr__(self, /):
        return type(self).__qualname__ + super().__repr__()

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_tuple(self, p, cycle, root=root)


class SetBase(tuple, CollectionBase):

    __slots__ = ()

    @classmethod
    def _yield_unique(cls, iterable, /):
        seen = set()
        for item in iterable:
            if item not in seen:
                yield item
                seen.add(item)

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, sorted(cls._yield_unique(
            map(cls.convert, iterable)
            )))

    def __repr__(self, /):
        return type(self).__qualname__ + super().__repr__()

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_tuple(self, p, cycle, root=root)


class DictBase(dict, CollectionBase):

    __slots__ = ()

    def __init__(self, /, *args, **kwargs):
        pre = dict(*args, **kwargs)
        convert = self.convert
        super().__init__(zip(
            map(convert, pre.keys()),
            map(convert, pre.values())
            ))

    @property
    def __setitem__(self, /):
        raise AttributeError

    @property
    def __delitem__(self, /):
        raise AttributeError

    def __hash__(self, /):
        return hash(tuple(self.items()))

    def __repr__(self, /):
        return type(self).__qualname__ + super().__repr__()

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_dict(self, p, cycle, root=root)


class ArrayBase(CollectionBase):

    __slots__ = ('_array',)

    def __init__(self, arg, /, dtype=None):
        if isinstance(arg, bytes):
            arr = _np.frombuffer(arg, dtype=dtype)
        else:
            arr = _np.array(arg, dtype=dtype).copy()
        self._array = arr

    for methname in (
            'dtype', 'shape', '__len__',
            ):
        exec('\n'.join((
            f"@property",
            f"def {methname}(self, /):",
            f"    return self._array.{methname}",
            )))
    del methname

    def __getitem__(self, arg, /):
        out = self._array[arg]
        if isinstance(out, _np.ndarray):
            return type(self)(out)
        return out

    def __repr__(self, /):
        content = _np.array2string(self._array, threshold=100)[:-1]
        return f"a({content})"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_array(self._array, p, cycle, root=root)

    def __hash__(self, /):
        return hash((bytes(self._array), self.dtype))


class DatMeta(UrMeta):
    ...


class Dat(Ur, metaclass=DatMeta):

    __slots__ = ()

    TYPS = (
        _Enum,
        type,
        _types.ModuleType,
        _types.FunctionType,
        _types.MethodType,
        _types.BuiltinFunctionType,
        _types.BuiltinMethodType,
        _functools.partial,
        classmethod,
        staticmethod,
        )

    @classmethod
    @_functools.lru_cache()
    def convert_type(cls, typ: type, /):
        if issubclass(typ, Dat):
            return typ
        if issubclass(typ, set):
            return DatSet
        if issubclass(typ, _np.ndarray):
            return DatArray
        if issubclass(typ, _collabc.Mapping):
            return DatDict
        if issubclass(typ, _collabc.Iterable):
            return DatTuple
        raise TypeError(typ)

    @classmethod
    def convert(cls, obj, /):
        if isinstance(obj, Dat):
            return obj
        return cls.convert_type(type(obj))(obj)


for typ in Dat.TYPS:
    Dat.register(typ)
del typ


class DatTuple(TupleBase, Dat):

    __slots__ = ()


class DatUniTuple(UniTupleBase, Dat):

    __slots__ = ()


class DatSet(SetBase, Dat):

    __slots__ = ()


class DatDict(DictBase, Dat):

    __slots__ = ()


class DatArray(ArrayBase, Dat):

    __slots__ = ()


@Dat.register
class Signifier:

    __slots__ = ('context', 'content')

    def __init__(self, context: Dat, content: str, /):
        self.context, self.content = Dat.convert(context), str(content)

    def __repr__(self, /):
        return f"Signifier({self.context}, {self.content})"


class Primitive(Dat):
    '''
    The abstract base class of all Python types
    that are acceptables as inputs
    to the Ptolemaic system.
    '''

    __slots__ = ()

    TYPS = (
        int,
        float,
        complex,
        str,
        bytes,
        bool,
        frozenset,
        type(None),
        type(Ellipsis),
        type(NotImplemented),
        )

    @classmethod
    @_functools.lru_cache()
    def convert_type(cls, typ: type, /):
        if issubclass(typ, Primitive):
            return typ
        if issubclass(typ, set):
            return PrimitiveSet
        if issubclass(typ, _collabc.Mapping):
            return PrimitiveDict
        if issubclass(typ, _collabc.Iterable):
            return PrimitiveTuple
        raise TypeError(typ)

    @classmethod
    def convert(cls, obj, /):
        if isinstance(obj, Primitive):
            return obj
        return cls.convert_type(type(obj))(obj)


for typ in Primitive.TYPS:
    Primitive.register(typ)
del typ


@DatTuple.register
class PrimitiveTuple(TupleBase, Primitive):

    __slots__ = ()


@DatUniTuple.register
class PrimitiveUniTuple(UniTupleBase, Primitive):

    __slots__ = ()


@DatSet.register
class PrimitiveSet(SetBase, Dat):

    __slots__ = ()


@DatDict.register
class PrimitiveDict(DictBase, Primitive):

    __slots__ = ()


class PseudoType(type):
    def __new__(meta, /, *args):
        name = f"{meta.__name__}{args}"
        return type.__new__(meta, name, (), dict(args=args))


class TypeIntersection(PseudoType):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(cls.__name__, cls.__bases__, cls.__dict__)

    def __subclasscheck__(cls, arg: type, /):
        for typ in cls.args:
            if not issubclass(arg, typ):
                return False
        return True

    def __instancecheck__(cls, arg: object, /):
        return cls.__subclasscheck__(type(arg))


class TypeBrace(PseudoType):

    def __new__(meta, overtyp, subtyps: tuple):
        subtyps = tuple(subtyps)
        return super().__new__(meta, overtyp, subtyps)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(cls.__name__, cls.__bases__, cls.__dict__)
        cls.__origin__, cls.__args__ = cls.args

    def __subclasscheck__(cls, typ: type, /):
        try:
            args = typ.__args__
            typ = typ.__origin__
        except AttributeError:
            return False
        if issubclass(typ, cls.__origin__):
            return all(
                issubclass(a, b)
                for a, b in zip(args, cls.__args__)
                )
        return False

    def __instancecheck__(cls, arg: tuple, /):
        try:
            args = tuple(map(type, arg))
        except TypeError:
            return False
        return cls.__subclasscheck__(type(arg)[args])


###############################################################################
###############################################################################
