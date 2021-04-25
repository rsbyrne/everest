
###############################################################################
'''Generic funcy structures.'''
###############################################################################

from abc import abstractmethod as _abstractmethod
from collections import abc as _collabc

from .abstract import FuncyABC as _FuncyABC
from . import datalike as _datalike
from . import exceptions as _exceptions

class FuncyContainer(_FuncyABC):
    ...
_ = FuncyContainer.register(_collabc.Container)

class FuncyIterable(_FuncyABC):
    ...
_ = FuncyIterable.register(_collabc.Iterable)

class FuncyIterator(_FuncyABC):
    ...
_ = FuncyIterator.register(_collabc.Iterator)

class FuncySized(_FuncyABC):
    ...
_ = FuncySized.register(_collabc.Sized)

class FuncyCallable(_FuncyABC):
    ...
_ = FuncyCallable.register(_collabc.Callable)

class FuncyCollection(FuncySized, FuncyIterable, FuncyContainer):
    ...
_ = FuncyCollection.register(_collabc.Collection)

class FuncyReversible(_FuncyABC):
    ...
_ = FuncyReversible.register(_collabc.Reversible)

class FuncySequence(FuncyReversible, FuncyCollection):
    ...
_ = FuncySequence.register(_collabc.Sequence)

class FuncyMutableSequence(FuncySequence):
    ...
_ = FuncyMutableSequence.register(_collabc.MutableSequence)

class FuncyMapping(FuncyCollection):
    ...
_ = FuncyMapping.register(_collabc.Mapping)

class FuncyUnpackable(_FuncyABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyUnpackable:
            if all((
                    issubclass(C, FuncyIterable),
                    not issubclass(C, FuncyMapping),
                    not issubclass(C, (tuple, str, _datalike.FuncyDatalike)),
                    )):
                return True
        return NotImplemented

class FuncyStruct(_FuncyABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyStruct:
            if all((
                    issubclass(C, FuncyCollection),
                    not issubclass(C, FuncyMutableSequence),
                    not issubclass(C, FuncyUnpackable),
                    not issubclass(C, FuncyMapping),
                    not issubclass(C, _datalike.FuncyString),
                    )):
                return True
        return NotImplemented
    @_abstractmethod
    def __len__(self):
        raise _exceptions.FuncyAbstractMethodException

###############################################################################
###############################################################################
