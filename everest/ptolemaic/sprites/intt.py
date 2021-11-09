###############################################################################
''''''
###############################################################################


import itertools as _itertools

from .sprite import Sprite as _Sprite
from . import exceptions as _exceptions


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


defaultexc = _exceptions.PtolemaicException()


class InttRange(_Sprite):

    _req_slots__ = ('_iterfn', '_lenfn', '_rangeobj')

    @classmethod
    def parameterise(cls, register, start, stop, step, /):
        register(
            (0 if start is None else int(start)),
            int(stop),
            (1 if step is None else int(step)),
            )

    def __init__(self, start, stop, step, /):
        super().__init__()
        rangeobj = self._rangeobj = range(start, stop, step)
        self._iterfn = rangeobj.__iter__
        self._lenfn = rangeobj.__len__

    def __iter__(self, /):
        return self._iterfn()

    def __len__(self, /):
        return self._lenfn()

    def __contains__(self, arg, /):
        if isinstance(arg, int):
            return arg in self._rangeobj
        return False

    def __str__(self, /):
        return ':'.join(map(str, (self.params.values())))

    def __getitem__(self, arg, /):
        if isinstance(arg, int):
            return self._rangeobj[arg]
        if arg is Ellipsis:
            return cls
        if isinstance(arg, slice):
            if arg.start is None and arg.stop is None and arg.step is None:
                return self
            nrang = self._rangeobj[arg]
            return InttRange(nrang.start, nrang.stop, nrang.step)
        raise TypeError(arg)


class InttCount(_Sprite):

    _req_slots__ = ('_iterfn',)

    @classmethod
    def parameterise(cls, register, start, step, /):
        register(
            (0 if start is None else int(start)),
            (0 if step is None else int(step)),
            )

    def __init__(self, start, stop, /):
        super().__init__()
        self._iterfn = _itertools.count(self.start, self.step).__iter__

    def __iter__(self, /):
        return self._iterfn()

    def __contains__(self, arg, /):
        if isinstance(arg, int):
            start, step = self.start, self.step
            return arg >= start and not (arg - start) % step
        return False

    def __str__(self, /):
        return f"{self.start}::{self.step}"

    def __getitem__(self, arg, /):
        if isinstance(arg, int):
            return _nth(self, arg)
        if arg is Ellipsis:
            return cls
        if isinstance(arg, slice):
            if arg.stop is None:
                if arg.start is None and arg.step is None:
                    return self
                start, nstart = self.start, arg.start
                if nstart is not None:
                    if nstart < 0:
                        raise ValueError(nstart)
                    start += int(nstart)
                step, nstep = self.step, arg.step
                if nstep is not None:
                    if nstep < 0:
                        raise ValueError(nstep)
                    step *= int(nstep)
                return InttCount(start, step)
            return (
                InttRange(self.start, arg.stop, self.step)
                [arg.start::arg.step]
                )
        raise TypeError(arg)


class Intt(_Sprite):

    @classmethod
    def construct(self, arg):
        return int(arg)

    @classmethod
    def _ptolemaic_getitem__(cls, arg, /):
        if isinstance(arg, int):
            return arg
        if arg is Ellipsis:
            return cls
        if isinstance(arg, slice):
            if arg.stop is None:
                if arg.start is None and arg.step is None:
                    return cls
                return InttCount(arg.start, arg.step)
            return InttRange(arg.start, arg.stop, arg.step)
        raise TypeError(arg)

    @classmethod
    def _ptolemaic_contains__(cls, arg, /):
        return isinstance(arg, int)


###############################################################################
###############################################################################
