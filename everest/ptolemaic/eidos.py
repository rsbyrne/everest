###############################################################################
''''''
###############################################################################


from .pleroma import Pleroma as _Pleroma
from .ousia import Ousia as _Ousia


class Eidos(_Ousia):

    def subclass(cls, /, *bases, name=None, **namespace):
        bases = (*bases, cls)
        if name is None:
            name = '_'.join(map(repr, bases))
        return type(name, bases, namespace)

    def _ptolemaic_contains__(cls, arg, /):
        return issubclass(type(arg), cls)

    def __contains__(cls, arg, /):
        return cls._ptolemaic_contains__(arg)

    def _ptolemaic_isinstance__(cls, arg, /):
        return issubclass(type(arg), cls)

    def __instancecheck__(cls, arg, /):
        return cls._ptolemaic_isinstance__(arg)

    def _ptolemaic_issubclass__(cls, arg, /):
        return super().__subclasscheck__(arg)

    def __subclasscheck__(cls, arg, /):
        return cls._ptolemaic_issubclass__(arg)

    def _ptolemaic_getitem__(cls, arg, /):
        if isinstance(arg, type):
            if issubclass(arg, cls):
                return arg
        raise TypeError(arg, type(arg))

    def __getitem__(cls, arg, /):
        return cls._ptolemaic_getitem__(arg)


###############################################################################
###############################################################################
