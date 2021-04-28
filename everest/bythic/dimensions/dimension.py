###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from collections import abc as _collabc

from . import _special, _wordhash

from .exceptions import *

def unpack_slice(slc):
    return (slc.start, slc.stop, slc.step)


class DimIterator(_collabc.Iterator):

    __slots__ = ('gen',)

    def __init__(self, iter_fn, /):
        self.gen = iter_fn()
        super().__init__()

    def __next__(self):
        return next(self.gen)

    def __repr__(self):
        return f"{__class__.__name__}({repr(self.gen)})"


def calculate_len(dim):
    raise NotYetImplemented

def raise_uniterable():
    raise DimensionUniterable

@_wordhash.Hashclass
class Dimension(_ABC):

    mroclasses = 'DimIterator'
    DimIterator = DimIterator

    __slots__ = ('_args', '_kwargs', 'args', 'kwargs', 'iterlen', 'iter_fn')

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._args = list()
        obj._kwargs = dict()
        return obj

    def __init__(self):
        if not hasattr(self, 'iterlen'):
            self.iterlen = _special.unkint
        if not hasattr(self, 'iter_fn'):
            self.iter_fn = raise_uniterable
        if not hasattr(self, '_args'):
            self._args = []
        if not hasattr(self, '_kwargs'):
            self._kwargs = dict()
        self.args = tuple(self._args)
        self.kwargs = tuple(self._kwargs.items())

    def __iter__(self):
        return DimIterator(self.iter_fn)

    def __len__(self):
        iterlen = self.iterlen
        if isinstance(self.iterlen, _special.Unknown):
            iterlen = self.iterlen = calculate_len(self)
        if isinstance(iterlen, _special.InfiniteInteger):
            raise DimensionInfinite
        return iterlen

    def __reduce__(self):
        return self._unreduce, self.args, self.kwargs

    @classmethod
    def _unreduce(cls, args, kwargs):
        return cls(*args, **dict(kwargs))

    def get_hashcontents(self):
        return (type(self), self.args, self.kwargs)

    # def __getitem__(self, arg):
    #     if isinstance(arg, slice):
    #         return ISlice(self, arg)
    #     if isinstance(arg, int):
    #         if arg < 0:
    #             arg = len(self) + arg
    #         return Collapsed(self, arg)
    #     raise TypeError(type(arg))


class Tandem(Dimension):

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


###############################################################################
###############################################################################
