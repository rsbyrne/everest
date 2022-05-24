###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc

import numpy as _np

from everest.utilities import pretty as _pretty

from .primitive import Primitive as _Primitive


class Ur(_abc.ABCMeta):
    ...


class DatMeta(Ur):
    ...


class Dat(metaclass=DatMeta):
    ...


_ = Dat.register(_Primitive)


def convert_type(typ: type, /):
    if issubclass(typ, Dat):
        return typ
    if issubclass(typ, _np.ndarray):
        return DatArray
    if issubclass(typ, _collabc.Mapping):
        return DatDict
    if issubclass(typ, _collabc.Iterable):
        return DatTuple
    raise TypeError(typ)

def convert(obj, /):
    if isinstance(obj, Dat):
        return obj
    return convert_type(type(obj))(obj)


class DatTuple(tuple, Dat):

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, map(convert, iterable))

    def __repr__(self, /):
        return type(self).__qualname__ + super().__repr__()

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_tuple(self, p, cycle, root=root)


class DatUniqueTuple(tuple, Dat):

    @classmethod
    def _yield_unique(cls, iterable, /):
        seen = set()
        for item in iterable:
            if item not in seen:
                yield item
                seen.add(item)

    def __new__(cls, iterable=(), /):
        return super().__new__(cls, cls._yield_unique(map(convert, iterable)))

    def __repr__(self, /):
        return type(self).__qualname__ + super().__repr__()

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_tuple(self, p, cycle, root=root)


class DatDict(dict, Dat):

    def __init__(self, /, *args, **kwargs):
        pre = dict(*args, **kwargs)
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


class DatArray(Dat):

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


###############################################################################
###############################################################################
