###############################################################################
'''General-purpose abstract classes.'''
###############################################################################

from abc import abstractmethod as _abstractmethod

from .abstract import FuncyABC as _FuncyABC
from .exceptions import FuncyAbstractMethodException

class FuncyEvaluable(_FuncyABC):
    '''
    Funcy Evaluables are immutable types hosting potentially immutable data,
    accessed through a .value property that may be cached.
    '''
    @property
    @_abstractmethod
    def value(self) -> None:
        '''The value of the evaluable.'''
        raise FuncyAbstractMethodException

class FuncyVariable(FuncyEvaluable):
    '''
    An Evaluable whose value may be manually changed
    using the descriptor protocol.
    '''
    @property
    @_abstractmethod
    def value(self) -> object:
        raise FuncyAbstractMethodException
    @value.setter
    def value(self, val) -> None:
        raise FuncyAbstractMethodException
    @value.deleter
    def value(self) -> None:
        self.value = None

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
