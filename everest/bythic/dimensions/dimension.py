###############################################################################
''''''
###############################################################################

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import abc as _collabc
from itertools import repeat as _repeat
from functools import partial as _partial, lru_cache as _lru_cache

from . import _special, _classtools

from .exceptions import (
    NotYetImplemented, DimensionUniterable, DimensionInfinite
    )


def calculate_len(dim):
    raise NotYetImplemented

def raise_uniterable():
    raise DimensionUniterable


class DimensionMeta(_ABCMeta):
    ...

@_classtools.Diskable
@_classtools.MROClassable
@_classtools.Operable
class Dimension(metaclass = DimensionMeta):

    __slots__ = ('iterlen', 'iter_fn', 'source', '_sourceget_')
    mroclasses = ('DimIterator', 'Derived', 'Transform', 'Slice')

    typ = object

    class Iterator(_collabc.Iterator):
        __slots__ = ('gen',)
        def __init__(self, iter_fn, /):
            self.gen = iter_fn()
            super().__init__()
        def __next__(self):
            return next(self.gen)
        def __repr__(self):
            return f"{__class__.__name__}({repr(self.gen)})"

    @_classtools.Overclass
    class Derived:
        fixedoverclass = None
        def __init__(self, *sources):
            source = None
            for source in sources:
                if isinstance(source, Dimension):
                    break
            if source is None:
                raise TypeError(
                    f"Source must be Dimension type, not {type(source)}"
                    )
            self.source = source
            if hasattr(source, '_sourceget_'):
                self._sourceget_ = source._sourceget_
            else:
                self._sourceget_ = type(source).__getitem__
            if not hasattr(self, 'iterlen'):
                self.iterlen = source.iterlen
            super().__init__()
            self.register_argskwargs(*sources) # pylint: disable=E1101
        def __getitem__(self, arg):
            return self._sourceget_(self, arg)

    class Transform(Derived):
        def __init__(self, operator, *operands):
            self.operands, self.operator = operands, operator
            if all(isinstance(op, Dimension) for op in operands):
                self.iter_fn = _partial(map, operator, *operands)
            else:
                getops = lambda: (
                    op if isinstance(op, Dimension) else _repeat(op)
                        for op in operands
                    )
                self.iter_fn = _partial(map, operator, *getops())
            super().__init__(operator, *operands)
    @classmethod
    def operate(cls, *args, **kwargs):
        return cls.Transform(*args, **kwargs)

    class Slice(Derived):
        def __init__(self, source, incisor, /):
            self.source, self.incisor = source, incisor
            super().__init__(source)
            self.register_argskwargs(incisor) # pylint: disable=E1101

    def __init__(self):
        if not hasattr(self, 'iterlen'):
            self.iterlen = None
        if not hasattr(self, 'iter_fn'):
            self.iter_fn = raise_uniterable
        super().__init__()

    @property
    def tractable(self):
        return self.iterlen < _special.inf

    def count(self, value):
        if not self.tractable:
            raise ValueError("Cannot count occurrences in infinite iterator.")
        i = 0
        for val in self:
            if val == value:
                i += 1
        return i

    def __iter__(self):
        return self.Iterator(self.iter_fn)

    def __len__(self):
        iterlen = self.iterlen
        if iterlen is None:
            self.iterlen = calculate_len(self)
            return self.__len__()
        if isinstance(iterlen, _special.InfiniteInteger):
            raise DimensionInfinite
        return iterlen

    def __bool__(self):
        iterlen = self.iterlen
        if iterlen is None:
            iterlen = self.iterlen = calculate_len(self)
        return iterlen > 0

    @_abstractmethod
    def __getitem__(self, arg):
        '''This class wouldn't be of much use without one of these!'''


class DimSet(Dimension):

    __slots__ = ('metrics',)

    def __init__(self, *args):
        metrics = []
        for arg in args:
            if isinstance(arg, tuple):
                metrics.extend(arg)
            elif isinstance(arg, Dimension):
                metrics.append(arg)
            else:
                raise TypeError(type(arg))
        metrics = self.metrics = tuple(metrics)
        self.iterlen = min(len(met) for met in metrics)
        self.iter_fn = lambda: zip(*self.metrics)
        super().__init__()
        self.register_argskwargs(*metrics) # pylint: disable=E1101


###############################################################################
###############################################################################
