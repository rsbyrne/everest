###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod

from .primitive import Primitive as _Primitive


class Ousia(_ABCMeta):
    '''
    The deepest metaclass of the Ptolemaic system.
    '''

    def subclass(cls, name, /, *bases, **namespace):
        return type(cls)(name, (cls, *bases), namespace)

    def __class_getitem__(cls, arg, /):
        if isinstance(arg, Ousia):
            return arg
        if issubclass(arg, _Primitive):
            return arg
        raise TypeError(arg, type(arg))

    def __getitem__(cls, arg, /):
        return cls.__class_getitem__(arg)


class Blank(metaclass=Ousia):
    ...


###############################################################################
###############################################################################
