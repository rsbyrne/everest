###############################################################################
''''''
###############################################################################


import abc as _abc
import types as _types
from enum import Enum as _Enum


class PrimitiveMeta(_abc.ABCMeta):

    def __class_instancecheck__(cls, arg, /):
        return super().__instancecheck__(arg)

    def __instancecheck__(cls, arg, /):
        return cls.__class_instancecheck__(arg)


class Primitive(metaclass=PrimitiveMeta):
    '''
    The abstract base class of all Python types
    that are acceptables as inputs
    to the Ptolemaic system.
    '''

    TYPS = (
        int,
        float,
        complex,
        str,
        bytes,
        bool,
        type(None),
        type(Ellipsis),
        type(NotImplemented),
        _Enum,
        type,
        )

    @classmethod
    def __subclasshook__(cls, C, /):
        if cls is Primitive:
            if issubclass(C, cls.TYPS):
                return True
        return NotImplemented

    # @classmethod
    # def __class_instancecheck__(cls, arg, /):
    #     if cls is not Primitive:
    #         return NotImplemented
    #     if isinstance(arg, cls.TYPS):
    #         return True
    #     if isinstance(arg, tuple):
    #         return all(map(cls.__instancecheck__, arg))
    #     if isinstance(arg, dict):
    #         return all(map(
    #             cls.__instancecheck__,
    #             (tuple(arg), tuple(arg.values())),
    #             ))
    #     if hasattr(arg, '__module__'):
    #         return arg.__module__ == 'builtins'
    #     return False


###############################################################################
###############################################################################
