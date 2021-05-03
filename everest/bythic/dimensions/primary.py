###############################################################################
''''''
###############################################################################

from functools import partial as _partial
from collections.abc import Iterable as _Iterable

from . import _special, _reseed

from .dimension import Dimension as _Dimension
from .slices import (
    ISlice as _ISlice,
    Selection as _Selection,
    Collapsed as _Collapsed,
    )
from .utilities import unpack_slice


class Primary(_Dimension):
    def __getitem__(self, arg):
        if isinstance(arg, slice):
            return _ISlice(self, arg)
        if isinstance(arg, _Iterable):
            if not isinstance(arg, _Dimension):
                arg = Arbitrary.construct(arg)
            return _Selection(self, arg)
        return _Collapsed(self, arg)

class Arbitrary(Primary):

    __slots__ = ('content',)

    def __init__(self, iterable, **kwargs):
        content = self.content = tuple(iterable)
        self.iterlen = len(content)
        self.iter_fn = content.__iter__
        super().__init__(**kwargs)
        self.register_argskwargs(content) # pylint: disable=E1101

    @classmethod
    def construct(cls, arg):
        typs = set()
        content = list()
        for ind, el in enumerate(arg):
            if ind > 1e9:
                raise ValueError("Iterable too long (> 1e9)")
            typs.add(type(el))
            content.append(el)
        if not content:
            raise ValueError("Empty iterable.")
        if len(typs) > 1:
            return Arbitrary(content)
        return Arbitrary(content, typ = tuple(typs)[0])


class Range(Primary):

    __slots__ = ('slc', 'start', 'stop', 'step', 'startinf', 'stopinf')
    Inf, inf, ninf = (_special.Infinite, None, None,)

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
    def construct(cls, *args):
        _, *args = unpack_slice(*args)
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
        return cls(*args)

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

    def __init__(self, arg0, arg1 = None, arg2 = None, /, **kwargs):
        self.slc, *args = unpack_slice(arg0, arg1, arg2)
        start, stop, step = self.proc_args(*args)
        startinf, stopinf = (isinstance(st, self.Inf) for st in (start, stop))
        self.start, self.stop, self.step, self.startinf, self.stopinf = \
            start, stop, step, startinf, stopinf
        self.iterlen = _special.infint
        super().__init__(**kwargs)
        self.register_argskwargs(start, stop, step) # pylint: disable=E1101


class Integral(Range):

    Inf, inf, ninf, typ = \
        _special.InfiniteInteger, _special.infint, _special.ninfint, int

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start, stop, step = self.start, self.stop, self.step
        if isinstance(step, str):
            self.iter_fn = _partial(rand_float_range, start, stop, step)
            self.iterlen = _special.infint
        elif not self.startinf:
            self.iter_fn = _partial(real_range, start, stop, step)
            if not self.stopinf:
                self.iterlen = int(abs(stop - start) // step) + 1


###############################################################################
###############################################################################
