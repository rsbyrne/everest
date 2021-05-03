###############################################################################
''''''
###############################################################################

from functools import partial as _partial
import itertools as _itertools
import math as _math

from . import _special

from .dimension import Dimension as _Dimension
from .utilities import unpack_slice


def selinds_iter(arb, inds):
    it = iter(inds)
    try:
        ind = next(it)
        for i, a in enumerate(arb):
            if i == ind:
                yield a
                ind = next(it)
    except StopIteration:
        return

def measure_boolean_selection(source, sliceinds):
    if sliceinds.iterlen > source.iterlen:
        return sliceinds[:len(source)].count(True)
    # so either both infinite or source is longer
    if sliceinds.tractable:
        return sliceinds.count(True)
    return _special.inf

def measure_integral_selection(source, sliceinds):
    return _special.unkint
    # if source.tractable:
    #     if not sliceinds.


class Selection(_Dimension.Slice):

    __slots__ = ('sliceinds',)

    def __init__(self, source, sliceinds):
        if not isinstance(sliceinds, _Dimension):
            raise TypeError(
                f"Selection argument must be Dimension type, "
                f"not {type(sliceinds)}"
                )
        if issubclass(sliceinds.typ, bool):
            self.iter_fn = _partial(_itertools.compress, source, sliceinds)
            self.iterlen = measure_boolean_selection(source, sliceinds)
        elif issubclass(sliceinds.typ, int):
            self.iter_fn = _partial(selinds_iter, source, sliceinds)
            self.iterlen = measure_integral_selection(source, sliceinds)
        else:
            raise TypeError("Only integral or boolean selections accepted.")
        super().__init__(source, sliceinds)


class Collapsed(_Dimension.Slice):

    __slots__ = '_val', 'ind', '_value'

    def __init__(self, dim, ind, /):
        self.ind, self._value, self.iterlen = ind, None, 1
        # self.iter_fn = _partial(iter, _partial(getattr, self, 'value'))
        self.iterlen = 1
        super().__init__(dim, ind)

    def __iter__(self):
        yield self.value

    @property
    def value(self):
        if (val := self._value) is None:
            for ind, val in enumerate(self.source):
                if ind == self.ind:
                    break
            self._value = val
        return val

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


class ISlice(_Dimension.Slice):

    __slots__ = 'start', 'stop', 'step'

    def __init__(self, dim, arg0, arg1 = None, arg2 = None, /):
        _, start, stop, step = unpack_slice(arg0, arg1, arg2)
        dimlen = dim.iterlen
        (start, stop, step), self.iterlen = \
            process_index_slice(start, stop, step, dimlen)
        self.start, self.stop = start, stop
        if step > 0:
            self.iter_fn = _partial(_itertools.islice, dim, start, stop, step)
        else:
            start = dimlen if start is None else start
            if start >= _special.inf:
                raise ValueError("Cannot reverse-slice from infinity.")
            abstep = abs(step)
            stop = 0 if stop is None else stop
            revstop, revstart = stop + abstep - 1, start + 1
            content = list(_itertools.islice(dim, revstop, revstart, abstep))
            content.reverse()
            self.iter_fn = content.__iter__
        step = None if step == 1 else step
        self.step = step
        super().__init__(dim, (start, stop, step))


###############################################################################
###############################################################################
