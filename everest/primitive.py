###############################################################################
''''''
###############################################################################


import abc as _abc
import types as _types
from enum import Enum as _Enum


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
    _types.FunctionType,
    _types.MethodType,
    _types.BuiltinFunctionType,
    _types.BuiltinMethodType,
    )


class Primitive(metaclass=_abc.ABCMeta):
    '''
    The abstract base class of all Python types
    that are acceptables as inputs
    to the Ptolemaic system.
    '''


for _typ in TYPS:
    Primitive.register(_typ)


###############################################################################
###############################################################################
