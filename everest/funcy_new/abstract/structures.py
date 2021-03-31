
###############################################################################
'''Generic funcy structures.'''
###############################################################################

from abc import abstractmethod as _abstractmethod

from .abstract import FuncyABC as _FuncyABC
from . import datalike as _datalike
from . import exceptions as _exceptions

class FuncyUnpackable(_FuncyABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyUnpackable:
            if all((
                    issubclass(C, _datalike.FuncyIterable),
                    not issubclass(C, _datalike.FuncyMapping),
                    not issubclass(C, (tuple, str, _datalike.FuncyDatalike)),
                    )):
                return True
        return NotImplemented

class FuncyStruct(_FuncyABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyStruct:
            if all((
                    issubclass(C, _datalike.FuncyCollection),
                    not issubclass(C, _datalike.FuncyMutableSequence),
                    not issubclass(C, FuncyUnpackable),
                    not issubclass(C, _datalike.FuncyMapping),
                    not issubclass(C, _datalike.FuncyString),
                    )):
                return True
        return NotImplemented
    @_abstractmethod
    def __len__(self):
        raise _exceptions.FuncyAbstractMethodException

###############################################################################
###############################################################################
