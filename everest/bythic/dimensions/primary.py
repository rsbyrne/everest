###############################################################################
''''''
###############################################################################

from functools import partial as _partial

from . import _special, _reseed

from .dimension import Dimension as _Dimension
from .utilities import unpack_slice


class Range(_Dimension):

    __slots__ = ('slc', 'start', 'stop', 'step', 'startinf', 'stopinf')
    Inf, inf, ninf, typ = _special.Infinite, None, None, object

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
        return super().__new__(cls)

    def __init__(self, arg0, arg1 = None, arg2 = None, /):
        self.slc, *args = unpack_slice(arg0, arg1, arg2)
        start, stop, step = self.proc_args(*args)
        startinf, stopinf = (isinstance(st, self.Inf) for st in (start, stop))
        self.start, self.stop, self.step, self.startinf, self.stopinf = \
            start, stop, step, startinf, stopinf
        self.iterlen = _special.infint
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
###############################################################################
