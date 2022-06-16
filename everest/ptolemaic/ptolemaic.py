###############################################################################
''''''
###############################################################################


import functools as _functools
from collections import abc as _collabc

import numpy as _np

from everest import ur as _ur


_Primitive = _ur.Primitive


_PSEUDOINSTANCES = (
    *_Primitive.TYPS,
    object,
    )


class PtolemaicMeta(_ur.DatMeta):

    def __instancecheck__(cls, other, /):
        if other in _PSEUDOINSTANCES:
            return True
        return super().__instancecheck__(other)


class Ptolemaic(_ur.Dat, metaclass=PtolemaicMeta):

    __slots__ = ()

    @classmethod
    @_functools.lru_cache()
    def convert_type(cls, typ: type, /):
        if issubclass(typ, Ptolemaic):
            return typ
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


convert_type = Ptolemaic.convert_type
convert = Ptolemaic.convert


Ptolemaic.register(PtolemaicMeta)
Ptolemaic.register(_Primitive)


@_ur.DatTuple.register
class PtolTuple(_ur.TupleBase, Ptolemaic):

    __slots__ = ()


@_ur.DatUniTuple.register
class PtolUniTuple(_ur.UniTupleBase, Ptolemaic):

    __slots__ = ()


@_ur.DatDict.register
class PtolDict(_ur.DictBase, Ptolemaic):

    __slots__ = ()


@_ur.DatArray.register
class PtolArray(_ur.ArrayBase, Ptolemaic):

    __slots__ = ()


###############################################################################
###############################################################################
