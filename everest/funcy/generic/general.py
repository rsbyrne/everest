###############################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod

from .exceptions import *

class FuncyGeneric(_ABC):
    ...

class FuncyNoneType(FuncyGeneric):
    ...
_ = FuncyNoneType.register(type(None))

class FuncySlice(FuncyGeneric):
    @_abstractmethod
    def indices(self, length: int, /) -> tuple:
        raise FuncyAbstractMethodException
    def iterable(self, length):
        return range(*self.indices(length))
_ = FuncySlice.register(slice)

class FuncyEvaluable(FuncyGeneric):
    @property
    @_abstractmethod
    def value(self):
        raise FuncyAbstractMethodException

class FuncyVariable(FuncyEvaluable):
    @property
    @_abstractmethod
    def value(self) -> object:
        raise FuncyAbstractMethodException
    @value.setter
    @_abstractmethod
    def value(self, val, /) -> None:
        raise FuncyAbstractMethodException
    @value.deleter
    def value(self) -> None:
        self.value = None

###############################################################################
