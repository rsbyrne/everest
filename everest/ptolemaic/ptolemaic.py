###############################################################################
''''''
###############################################################################


import functools as _functools

from everest import ur as _ur


_Primitive = _ur.Primitive


class Ptolemaic(_ur.Dat):

    __slots__ = ()

    @classmethod
    @_functools.lru_cache()
    def convert_type(cls, typ: type, /):
        if issubclass(typ, Ptolemaic):
            return typ
        if issubclass(typ, _Primitive):
            return typ
        raise TypeError(typ)

    @classmethod
    def convert(cls, obj, /):
        if isinstance(obj, (Ptolemaic, _Primitive)):
            return obj
        return cls.convert_type(type(obj))(obj)


###############################################################################
###############################################################################
