###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.ptolemaic.aspect import Aspect as _A
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.proxy import Proxy as _Proxy
from everest.ptolemaic.chora import Sliceable as _Sliceable
from everest.ptolemaic.eidos import Eidos as _Eidos


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


_OPINT = (type(None), int)


class InttRange(_Sprite, _Sliceable):

    _req_slots__ = (
        'start', 'stop', 'step',
        '_iterfn', '_lenfn', '_rangeobj', '_tupobj',
        )

    @classmethod
    def parameterise(cls, register,
            arg0, /, arg1=NotImplemented, arg2=NotImplemented
            ):
        if arg2 is NotImplemented:
            if arg1 is NotImplemented:
                start, stop, step = None, arg0, None
            else:
                start, stop, step = arg1, arg2, None
        else:
            start, stop, step = arg0, arg1, arg2
        register(
            (0 if start is None else int(start)),
            int(stop),
            (1 if step is None else int(step)),
            )

    def __init__(self, start, stop, step=1, /):
        super().__init__()
        self.start, self.stop, self.step = start, stop, step
        rangeobj = self._rangeobj = range(start, stop, step)
        tupobj = self._tupobj = tuple(rangeobj)
        self._iterfn = tupobj.__iter__
        self._lenfn = tupobj.__len__

    def __iter__(self, /):
        return self._iterfn()

    def __len__(self, /):
        return self._lenfn()

    def __reversed__(self, /):
        return self[::-1]

    def __instancecheck__(self, val: int, /):
        return val in self._rangeobj

    def _incise_slice_nontrivial_(self,
            start: _OPINT, stop: _OPINT, step: _OPINT, /
            ):
        nrang = self._rangeobj[start:stop:step]
        return InttRange(nrang.start, nrang.stop, nrang.step)

    def _retrieve_contains_(self, incisor: int, /) -> int:
        return self._tupobj[incisor]

    def __str__(self, /):
        return ':'.join(map(str, (self.params.values())))


class InttCount(_Sprite, _Sliceable):

    _req_slots__ = (
        'start', 'step',
        '_iterfn',
        )

    @classmethod
    def parameterise(cls, register,
            arg0=NotImplemented, arg1=NotImplemented, /
            ):
        if arg1 is NotImplemented:
            start, stop = None, arg0
        else:
            start, stop = arg0, arg1
        register(
            (0 if start is None else int(start)),
            (1 if step is None else int(step)),
            )

    def __init__(self, start, step, /):
        super().__init__()
        self.start, self.step = start, step
        self._iterfn = _itertools.count(start, step).__iter__

    def __instancecheck__(self, val: int, /):
        start, step = self.start, self.step
        return val >= start and not (val - start) % step

    def _incise_slice_open_(self,
            start: int, stop: type(None), step: _OPINT, /
            ):
        pstart, pstep = self.start, self.step
        if start is not None:
            if start < 0:
                raise ValueError(start)
            pstart += int(start)
        if step is not None:
            if step < 0:
                raise ValueError(step)
            pstep *= int(step)
        return InttCount(pstart, pstep)

    def _incise_slice_closed_(self,
            start: _OPINT, stop: int, step: _OPINT, /
            ):
        return InttRange(self.start, stop, self.step)[start::step]

    def _retrieve_contains_(self, incisor: int, /) -> int:
        if incisor >= 0:
            return _nth(self, incisor)
        return super()._retrieve_contains_(incisor)

    def __iter__(self, /):
        return self._iterfn()

    def __str__(self, /):
        return f"{self.start}::{self.step}"


class InttSpace(_Sliceable):

    def _retrieve_contains_(self, incisor: int, /) -> int:
        return Intt(incisor)

    def _incise_slice_open_(self,
            start: int, stop: type(None), step: _OPINT, /
            ):
        return InttCount(start, step)

    def _incise_slice_closed_(self,
            start: _OPINT, stop: int, step: _OPINT, /
            ):
        return InttRange(start, stop, step)


class Intt(metaclass=_Eidos):

    @classmethod
    def _get_clschora(cls, /) -> _Sliceable:
        return InttSpace()

    @classmethod
    def _ptolemaic_isinstance__(self, val, /):
        return isinstance(val, int)

    @classmethod
    def construct(cls, arg, /):
        return int(arg)


###############################################################################
###############################################################################
