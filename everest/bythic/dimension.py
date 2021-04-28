###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from collections import abc as _collabc
from functools import partial as _partial
import itertools as _itertools
import math as _math

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
        if isinstance(arg, int):
            if arg < 0:
                arg = len(self) + arg
            return Collapsed(self, arg)
        raise TypeError(type(arg))


class Derived(Dimension):

    __slots__ = ('source',)

    def __init__(self, source, /):
        self.source = source
        self.iterlen = source.iterlen
        super().__init__()


class Collapsed(Derived):
    __slots__ = ('_val', 'ind',)
    def __init__(self, dim, ind, /):
        super().__init__(dim)
        self.ind, self._value, self.iterlen = ind, None, 1
    @property
    def value(self):
        if (val := self._value) is None:
            for ind, val in enumerate(self.source):
                if ind == self.ind:
                    break
            self._value = val
        return val
    def iter_fn(self):
        yield self.value


def process_negative_index(ind, dimlen):
    if ind is None:
        return ind
    if ind < 0:
        if dimlen < _special.inf:
            return dimlen + ind
        raise ValueError(
            "Cannot process negative indices on infinite iterator."
            )
    return ind

def get_slice_length(start, stop, step, /, dimlen = _special.inf):
    start, stop, step = slice(start, stop, step).indices(dimlen)
    if step < 0:
        if start is None:
            start = dimlen - 1
        if stop is None:
            stop = 0
        span = start - stop
    elif step > 0:
        if start is None:
            start = 0
        if stop is None:
            stop = dimlen
        span = stop - start
    else:
        raise ValueError(step)
    span = max(0, span)
    if span < (inf := _special.inf):
        return _math.ceil(span / abs(step))
    return inf

def process_index_slice(start, stop, step, /, dimlen = _special.inf):
    step = 1 if step is None else step
    if not abs(step) < _special.inf:
        raise ValueError
    if step == 0:
        raise ValueError
    if isinstance(start, _special.Infinite):
        raise ValueError("Infinite start index.")
    start, stop = (process_negative_index(st, dimlen) for st in (start, stop))
    inf = _special.inf
    maxind = dimlen - 1
    nullslc = 0, 0, None
    if step > 0:
        if start is not None:
            if start > maxind or start == inf:
                return nullslc, 0
            if start == 0:
                start = None
        if stop is not None:
            if stop == 0:
                return nullslc, 0
            if stop > maxind + 1 or stop == inf:
                stop = None
    elif step < 0:
        if start is not None:
            if start == 0:
                return nullslc, 0
            if start >= maxind or start == inf:
                start = None
        if stop is not None:
            if stop >= maxind or stop == inf:
                return nullslc, 0
    length = get_slice_length(start, stop, step, dimlen)
    return (start, stop, step), length


class ISlice(Derived):

    __slots__ = 'start', 'stop', 'step'

    def __init__(self, dim, arg0, arg1 = None, arg2 = None, /):
        super().__init__(dim)
        _, start, stop, step = Range.unpack_slice(arg0, arg1, arg2)
        dimlen = dim.iterlen
        (start, stop, step), self.iterlen = \
            process_index_slice(start, stop, step, dimlen)
        if step > 0:
            self.iter_fn = _partial(_itertools.islice, dim, start, stop, step)
        else:
            abstep = abs(step)
            sstart = dimlen if start is None else start
            sstop = 0 if stop is None else stop
            revstop, revstart = sstop + abstep - 1, sstart + 1
            content = list(_itertools.islice(dim, revstop, revstart, abstep))
            content.reverse()
            self.iter_fn = content.__iter__
        step = None if step == 1 else step
        self.start, self.stop, self.step = start, stop, step


class Transform(Derived):

    __slots__ = 'operator', 'operant'

    def __init__(self, operant, operator, /):
        super().__init__(operant)
        self.operator = operator
        self.iter_fn = self.get_iterfn(operator, operant)

    @staticmethod
    def get_iterfn(operator, operant):
        return _partial(map, operator, operant)


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
    Inf, inf, ninf, typ = _special.Infinite, None, None, object

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
        if isinstance(step, cls.typ):
            start = cls.proc_arg(start, step)
            stop = cls.proc_arg(stop, step, inv = True)
            if any((
                    (step > 0 and start > stop),
                    (step < 0 and start < stop),
                    start == stop
                    )):
                raise ValueError("Zero-length range.")
            return start, stop, step
        return cls.typ(start), cls.typ(stop), step

    def __new__(cls, *args):
        _, *args = cls.unpack_slice(*args)
        if cls is Range:
            start, stop, step = args
            if isinstance(step, float):
                return Real(*args)
            if isinstance(step, int):
                return Integral(*args)
            if any(
                    isinstance(st, (cls.Inf, type(None)))
                        for st in (start, stop)
                    ):
                raise ValueError(
                    "Cannot have an open range with a non-finite step"
                    )
            if any(isinstance(st, float) for st in (start, stop)):
                return Real(*args)
            return Integral(*args)
        return super().__new__(cls)

    def __init__(self, arg0, arg1 = None, arg2 = None, /):
        self.slc, *args = self.unpack_slice(arg0, arg1, arg2)
        start, stop, step = self.proc_args(*args)
        startinf, stopinf = (isinstance(st, self.Inf) for st in (start, stop))
        self.start, self.stop, self.step, self.startinf, self.stopinf = \
            start, stop, step, startinf, stopinf
        self.iterlen = self.inf
        super().__init__()


class Integral(Range):

    Inf, inf, ninf, typ = \
        _special.InfiniteInteger, _special.infint, _special.ninfint, int

    def __init__(self, *args):
        super().__init__(*args)
        start, stop, step = self.start, self.stop, self.step
        if isinstance(step, str):
            choices = list(range(start, stop))
            _reseed.rshuffle(choices, seed = step)
            self.iter_fn = choices.__iter__
            self.iterlen = len(choices)
        elif not self.startinf:
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

def rand_float_range(start, stop, seed):
    rsd = _reseed.Reseed(seed)
    while True:
        yield rsd.rfloat(start, stop)

class Real(Range):

    Inf, inf, ninf, typ = \
        _special.InfiniteFloat, _special.infflt, _special.ninfflt, float

    def __init__(self, *args):
        super().__init__(*args)
        start, stop, step = self.start, self.stop, self.step
        if isinstance(step, str):
            self.iter_fn = _partial(rand_float_range, start, stop, step)
            self.iterlen = _special.infint
        elif not self.startinf:
            self.iter_fn = _partial(real_range, start, stop, step)
            if not self.stopinf:
                self.iterlen = int(abs(stop - start) // step) + 1

###############################################################################

# def inquirer(start, stop, step, dimlen):
#     print((start, stop, step), dimlen)
#     mylist = list(range(dimlen))
#     print("incorrect length:", get_slice_length(start, stop, step, dimlen))
#     mycut = mylist[start:stop:step]
#     print("correct length:", len(mycut))
#     start, stop, step = proper = slice(start, stop, step).indices(dimlen)
#     print("proper indices:", proper)
#     print(mycut)
#
# for dimlen in range(10):
#     alist = list(range(dimlen))
#     for start in range(-10, 10):
#         for stop in range(-10, 10):
#             for step in range(-10, 10):
#                 if not step:
#                     continue
#                 a = len(alist[start: stop: step])
#                 b = get_slice_length(start, stop, step, dimlen)
#                 if a != b:
#                     inquirer(start, stop, step, dimlen)
#                     print('\n')

#             for step in range(-3, 3):
#                 if not step == 0:
#                     a = len(alist[start:stop:step])
#                     b = get_slice_length(sstart, sstop, step, dimlen)
#                     if a != b:
#                         print(a, b, (start, stop, step), dimlen)
#                     assert a == b, (a, b, (start, stop, step), dimlen)
#                     a = len(list(range(dimlen))[start:stop:step])
#                     b = get_slice_length(start, stop, step, dimlen)
#                     if a != b:
#                         print(a, b, (start, stop, step), dimlen)

# mydim = Transform(Range(10, 30, 1.5), round)[3: 9] -> [14, 16, 18, 19, 20, 22]


###############################################################################
