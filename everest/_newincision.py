###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod
from collections import abc as _collabc
from functools import partial as _partial
import itertools as _itertools

from everest import mroclasses as _mroclasses
from everest import special as _special
from everest import exceptions as _exceptions

class DimensionException(_exceptions.EverestException):
    '''Base class for special exceptions raised by Dimension classes.'''
class DimensionUniterable(DimensionException):
    '''This dimension cannot be iterated over.'''
class DimensionInfinite(DimensionException):
    '''This dimension is infinitey long.'''

def unpack_slice(slc):
    return (slice.start, slice.stop, slice.step)

class DimIterator(_collabc.Iterator):
    __slots__ = 'gen', '__next__'
    def __init__(self, iter_fn, /):
        gen = self.gen = iter_fn()
        self.__next__ = gen.__next__
        super().__init__()
    def __repr__(self):
        return f"{__class__.__name__}({repr(self.gen)})"

def calculate_len(dim):
    raise _exceptions.NotYetImplemented

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

class Derived(Dimension):
    __slots__ = 'source',
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
    def get_iterfn(cls, operator, operant):
        return _partial(map, operator, operant)

class ISlice(Derived):
    __slots__ = 'dim', 'start', 'stop', 'step'
    def __init__(self, dim, arg0, arg1 = None, arg2 = None, /):
        super().__init__(dim)
        slc, start, stop, step = Range.unpack_slice(arg0, arg1, arg2)
        dimlen = dim.iterlen
        step = 1 if step is None else step
        if step == 0:
            raise ValueError
        elif not abs(step) < _special.inf:
            raise ValueError
        elif step > 0:
            if start == _special.inf:
                raise ValueError
            elif start == _special.ninf:
                start = 0
            if stop == _special.ninf:
                raise ValueError
            elif stop == _special.inf:
                stop = None
        elif step < 0:
            if dimlen == _special.inf:
                raise ValueError
            if start == _special.ninf:
                raise ValueError
            elif start == _special.inf:
                start = -1
            if stop == _special.inf:
                raise ValueError
            elif stop == _special.ninf:
                stop = None
        else:
            raise ValueError
        step = int(step)
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
        self.iterlen = 1
        super().__init__()
    def iter_fn(self):
        yield metric

class Tandem(Dimension):
    __slots__ = 'metrics'
    def __init__(self, *args):
        metrics = []
        for arg in args:
            if isinstance(arg, tuple):
                metrics.extend(arg)
            elif isinstance(arg, Dimension):
                metrics.append(arg)
            else:
                raise TypeError(type(arg))
        self.metrics = tuple(metrics)
        super().__init__()
    def iter_fn(self):
        return zip(self.metrics)

class Range(Dimension):
    __slots__ = 'slc', 'start', 'stop', 'step',
    Inf, inf, ninf, typ = None, None, None, None
    @classmethod
    def unpack_slice(cls, arg0, arg1 = None, arg2 = None, /):
        if isinstance(arg0, slice):
            if any(arg is not None for arg in (arg1, arg2)):
                raise ValueError("Cannot provide both slice and args.")
            slc = arg0
        else:
            slc = slice(arg0, arg1, arg2)
        return slc, slc.start, slc.stop, slc.step
    def __new__(cls, *args):
        slc, *args = cls.unpack_slice(*args)
        if cls is Range:
            if any(isinstance(arg, float) for arg in args):
                return Real(*args)
            else:
                return Integral(*args)
        else:
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

class Real(Range):
    Inf, inf, ninf, typ = \
        _special.InfiniteFloat, _special.infflt, _special.ninfflt, float
    def __init__(self, *args):
        super().__init__(*args)
        start, stop, step = self.start, self.stop, self.step
        if not self.startinf:
            self.iter_fn = _partial(real_range, start, stop, step)
            self.iterlen = int(abs(stop - start) // step) + 1

# class Analytical(Dimension):

###############################################################################
###############################################################################

# class Slyce:
#     __slots__ = 'slice', 'start', 'stop', 'step'
#     def __init__(self, arg0, arg1 = None, arg2 = None, /):
#         if isinstance(arg0, slice):
#             if not all(arg is None for arg in (arg1, arg2)):
#                 raise ValueError("Cannot provide both slice and args.")
#             self.slc = arg0
#             self.start, self.stop, self.step = arg0.start, arg0.stop, arg0.step
#         else:
#             self.start, self.stop, self.step = arg0, arg1, arg2
#             self.slc = slice(arg0, arg1, arg2)
#         super().__init__()

###############################################################################
''''''
###############################################################################

class Space:
    '''Instances of this class represent spaces.'''
    __slots__ = 'dimensions',
    def __init__(self, *dimensions):
        self.dimensions = dimensions

###############################################################################
###############################################################################

###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod

from everest import special as _special
from everest import mroclasses as _mroclasses

def process_depth(
        args: tuple, depth: int, /,
        filler = None,
        ):
    args = tuple(arg if arg != slice(None) else filler for arg in args)
    if (not depth < _special.infint) and (Ellipsis in args):
        raise ValueError("Cannot use ellipsis when depth is infinite.")
    nargs = len(args)
    if nargs == 0:
        return args
    if nargs == 1:
        if args[0] is Ellipsis:
            return tuple(filler for _ in range(depth))
        return args
    if nargs < depth:
        nellipses = len(tuple(el for el in args if el is Ellipsis))
        if nellipses == 0:
            return args
        if nellipses == 1:
            out = []
            for arg in args:
                if arg is Ellipsis:
                    for _ in range(depth - nargs):
                        out.append(filler)
                else:
                    out.append(arg)
            return tuple(out)
        raise IndexError(f"Too many ellipses ({nellipses} > 1)")
    if nargs == depth:
        return tuple(filler if arg is Ellipsis else arg for arg in args)
    raise IndexError(
        f"Not enough depth to accommodate requested levels:"
        f" levels = {nargs} > depth = {depth})"
        )

@_mroclasses.Overclass
class Incision:
    '''An object that can be 'incised'.'''
    __slots__ = 'source', 'incisors', 'depth', '__getitem__'
    def __new__(cls, source, **incisors):
        obj = super().__new__(cls)

    def __init__(self, source, **incisors):
        self.source = source
        self.incisors = incisors
        super().__init__()
    def __getitem__(self, incisors):
        if isinstance(incisors, dict):
            return self.incise(**incisors)
        if isinstance(incisors, tuple):
            incisors = process_depth(incisors, len(self.incisors))
        else:
            incisors = (incisors,)
        return self.incise(**dict(zip(self.incisors, incisors)))
    def incise(self, **incisors):
        newincs = {**self.incisors}
        for dimname, incisor in incisors.items():
            if incisor is None:
                continue
            preinc = newincs[dimname]
            if preinc is None:
                newinc = incisor
            elif isinstance(preinc, tuple):
                newinc = (*preinc, incisor)
            else:
                newinc = (preinc, incisor)
            newincs[dimname] = newinc
        return type(self)(self.source, **newincs)
    def __repr__(self):
        return f"{repr(self.source)}_{type(self).__name__}[{self.incisors}]"

@property
def get_incision(obj):
    try:
        return obj._incision
    except AttributeError:
        incision = obj._incision = obj.Incision(obj)
        return incision
@property
def get_getitem(obj):
    return obj.incision.__getitem__
@property
def get_incise(obj):
    return obj.incision.incise

class Incisable(_mroclasses.MROClassable):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is Incisable:
            try:
                Inc = getattr(cls, 'Incision')
                if issubclass(Inc, Incision) and issubclass(Inc, C):
#                     if 'resol'
                    return True
            except AttributeError:
                pass
        return NotImplemented
    def __new__(cls, ACls):
        '''Class decorator for designating an Incisable.'''
        ACls = super().__new__(cls, ACls)
        if not hasattr(ACls, 'Incision'):
            setattr(ACls, 'Incision', Incision)
        if not hasattr(ACls, 'incision'):
            ACls.incision = get_incision
        if not hasattr(ACls, '__getitem__'):
            ACls.__getitem__ = get_getitem
        if not hasattr(ACls, 'incise'):
            ACls.incise = get_incise
        return ACls

###############################################################################
###############################################################################

# mylist = list(range(10))
# myobj = Incisable(mylist, foo = None, bah = None, qux = None, qin = None)
# display(myobj)
# myobj = myobj.incise(foo = 10)
# display(myobj)
# myobj = myobj.incise(foo = 'a', bah = 'banana')
# display(myobj)
# myobj = myobj[1, ..., 3]
# display(myobj)
