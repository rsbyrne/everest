###############################################################################
'''General-purpose abstract classes.'''
###############################################################################

from abc import abstractmethod as _abstractmethod

from .abstract import FuncyABC as _FuncyABC
from .exceptions import FuncyAbstractMethodException

class FuncyEvaluable(_FuncyABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyEvaluable:
            if any('value' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

def evaluable(arg):
    return isinstance(arg, FuncyEvaluable)

class FuncyVariable(FuncyEvaluable):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyVariable:
            if any('set_value' in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

class FuncyNoneType(_FuncyABC):
    ...
_ = FuncyNoneType.register(type(None))

class FuncySlice(_FuncyABC):
    @_abstractmethod
    def indices(self, length: int, /) -> tuple:
        raise FuncyAbstractMethodException
    def iterable(self, length):
        return range(*self.indices(length))
_ = FuncySlice.register(slice)

###############################################################################
###############################################################################
