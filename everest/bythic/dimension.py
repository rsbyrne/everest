###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from collections import abc as _collabc
from functools import partial as _partial
import itertools as _itertools

from . import _special, _reseed

from .exceptions import BythicException, NotYetImplemented


class DimensionException(BythicException):
    '''Base class for special exceptions raised by Dimension classes.'''
class DimensionUniterable(DimensionException):
    '''This dimension cannot be iterated over.'''
class DimensionInfinite(DimensionException):
    '''This dimension is infinitely long.'''


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


class Dimension(_ABC):

    mroclasses = 'DimIterator'
    DimIterator = DimIterator
    iterlen = _special.unkint
    iter_fn = raise_uniterable

    def __iter__(self):
        return DimIterator(self.iter_fn)

    def __len__(self):
        iterlen = self.iterlen
        if isinstance(iterlen, _special.InfiniteInteger):
            raise DimensionInfinite
        if isinstance(iterlen, _special.Unknown):
            iterlen = self.iterlen = calculate_len(self)
        return iterlen

    def __getitem__(self, arg):
        if isinstance(arg, slice):
            return ISlice(self, arg)
        raise TypeError(type(arg))


class Derived(Dimension):

    __slots__ = ('source',)

    def __init__(self, source, /):
        self.source = source
        self.iterlen = source.iterlen
        super().__init__()


class Transform(Derived):

    __slots__ = 'operator', 'operant'

    def __init__(self, operant, operator, /):
        super().__init__(operant)
        self.operator = operator
        self.iter_fn = self.get_iterfn(operator, operant)

    @staticmethod
    def get_iterfn(operator, operant):
        return _partial(map, operator, operant)


class ISlice(Derived):

    __slots__ = 'dim', 'start', 'stop', 'step'

    @staticmethod
    def islice_process_args(start, stop, step, dimlen):
        step = 1 if step is None else step
        if step == 0:
            raise ValueError
        if not abs(step) < _special.inf:
            raise ValueError
        if step > 0:
            if start == _special.inf:
                raise ValueError
            if start == _special.ninf:
                start = 0
            if stop == _special.ninf:
                raise ValueError
            if stop == _special.inf:
                stop = None
        elif step < 0:
            if dimlen == _special.inf:
                raise ValueError
            if start == _special.ninf:
                raise ValueError
            if start == _special.inf:
                start = -1
            if stop == _special.inf:
                raise ValueError
            if stop == _special.ninf:
                stop = None
        else:
            raise ValueError
        step = int(step)
        return start, stop, step

    def __init__(self, dim, arg0, arg1 = None, arg2 = None, /):
        super().__init__(dim)
        slc, start, stop, step = Range.unpack_slice(arg0, arg1, arg2)
        dimlen = dim.iterlen
        start, stop, step = self.islice_process_args(start, stop, step, dimlen)
        slc = slice(start, stop, step)
        if dimlen < _special.inf:
            self.iterlen = len(range(*slc.indices(dimlen)))
        else:
            if stop is None:
                self.iterlen = dimlen
            else:
                self.iterlen = len(range(start, stop, step))
        self.iter_fn = _partial(_itertools.islice, dim, start, stop, step)


class Collapsed(Dimension):
    def __init__(self, metric0, *metricn):
        self.metric = (metric0, *metricn) if metricn else metric0
        self.iter_fn = lambda: (met for met in (self.metric,))
        self.iterlen = 1
        super().__init__()


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
        super().__init__()

    def iter_fn(self):
        return zip(*self.metrics)


class Range(Dimension):

    __slots__ = ('slc', 'start', 'stop', 'step',)
    Inf, inf, ninf, typ = _special.Infinite, None, None, lambda x: x

    @classmethod
    def unpack_slice(cls, arg0, arg1 = None, arg2 = None, /):
        if isinstance(arg0, slice):
            if any(arg is not None for arg in (arg1, arg2)):
                raise ValueError("Cannot provide both slice and args.")
            slc = arg0
        else:
            slc = slice(arg0, arg1, arg2)
        return slc, slc.start, slc.stop, slc.step

    @classmethod
    def proc_arg(cls, arg, step, inv = False):
        if arg is None:
            if inv:
                lower, upper = cls.inf, cls.ninf
            else:
                lower, upper = cls.ninf, cls.inf
            return lower if step > 0 else upper
        if isinstance(arg, cls.Inf):
            return arg
        return cls.typ(arg)

    @classmethod
    def proc_args(cls, start, stop, step, stepdefault = 1):
        step = stepdefault if step is None else step
        step = cls.typ(step)
        start = cls.proc_arg(start, step)
        stop = cls.proc_arg(stop, step, inv = True)
        if any(clauses := (
                (step > 0 and start > stop),
                (step < 0 and start < stop),
                start == stop
                )):
            print(start, stop, step, clauses)
            raise ValueError("Zero-length range.")
        return start, stop, step

    def __new__(cls, *args):
        _, *args = cls.unpack_slice(*args)
        if cls is Range:
            if any(isinstance(arg, float) for arg in args):
                return Real(*args)
            return Integral(*args)
        return super().__new__(cls)

    def __init__(self, arg0, arg1 = None, arg2 = None, /):
        self.slc, *args = self.unpack_slice(arg0, arg1, arg2)
        start, stop, step = self.proc_args(*args)
        startinf, stopinf = (isinstance(st, self.Inf) for st in (start, stop))
        if startinf or stopinf:
            self.iterlen = self.inf
        self.start, self.stop, self.step, self.startinf, self.stopinf = \
            start, stop, step, startinf, stopinf
        super().__init__()


class Integral(Range):

    Inf, inf, ninf, typ = \
        _special.InfiniteInteger, _special.infint, _special.ninfint, int

    def __init__(self, *args):
        super().__init__(*args)
        start, stop, step = self.start, self.stop, self.step
        if not self.startinf:
            rang = self.rang = range(start, stop, step)
            self.iter_fn = rang.__iter__
            if not self.stopinf:
                self.iterlen = len(rang)

    def indices(self, n):
        return self.slc.indices(n)

def real_range(incrementer, stop, step):
    while incrementer < stop:
        yield incrementer
        incrementer += step

def random_stride(start, stop, seed):
    mag = stop - start
    with _reseed.Reseed(seed = seed).rng as rng:




class Real(Range):

    __slots__ = ()
    Inf, inf, ninf, typ = \
        _special.InfiniteFloat, _special.infflt, _special.ninfflt, float

    def __init__(self, *args):
        super().__init__(*args)
        start, stop, step = self.start, self.stop, self.step
        if isinstance(step, str):
            if self.startinf or self.stopinf:
                raise ValueError("Cannot random-stride an unbounded range.")

        if not self.startinf:
            self.iter_fn = _partial(real_range, start, stop, step)
            self.iterlen = int(abs(stop - start) // step) + 1

# class Analytical(Dimension):

###############################################################################
###############################################################################

# mydim = Transform(Range(10, 30, 1.5), round)[3: 9] -> [14, 16, 18, 19, 20, 22]
