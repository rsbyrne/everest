###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.chora import (
    Sliceable as _Sliceable, Incision as _Incision
    )


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


_OPINT = (type(None), int)


class InttRange(_Sliceable):

    _req_slots__ = ('_iterfn', '_lenfn', '_rangeobj', '_tupobj',)

    start: int
    stop: int
    step: int = 1

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = super().parameterise(*args, **kwargs)
        start, stop, step = bound.args
        if start is None:
            bound.arguments['start'] = 0
        if step is None:
            bound.arguments['step'] = 1
        return bound

    def __init__(self, /):
        super().__init__()
        rangeobj = self._rangeobj = range(self.start, self.stop, self.step)
        tupobj = self._tupobj = tuple(rangeobj)
        self._iterfn = tupobj.__iter__
        self._lenfn = tupobj.__len__

    def __iter__(self, /):
        return self._iterfn()

    def __len__(self, /):
        return self._lenfn()

    def __reversed__(self, /):
        return self[::-1]

#     def __instancecheck__(self, val: int, /):
#         return val in self._rangeobj

    def slice_incise_nontrivial(self, incisor: (_OPINT, _OPINT, _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        nrang = self._rangeobj[start:stop:step]
        return InttRange(nrang.start, nrang.stop, nrang.step)

    def retrieve_contains(self, incisor: int, /) -> int:
        return self._tupobj[incisor]

    def __str__(self, /):
        return ':'.join(map(str, self.args))


class InttCount(_Sliceable):

    _req_slots__ = ('_iterfn',)

    start: int
    step: int

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = super().parameterise(*args, **kwargs)
        start, step = bound.args
        if start is None:
            bound.arguments['start'] = 0
        if step is None:
            bound.arguments['step'] = 1
        return bound

    def __init__(self, /):
        super().__init__()
        self._iterfn = _itertools.count(self.start, self.step).__iter__

#     def __instancecheck__(self, val: int, /):
#         start, step = self.start, self.step
#         return val >= start and not (val - start) % step

    def slice_incise_open(self, incisor: (int, type(None), _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
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

    def slice_incise_closed_(self, incisor: (_OPINT, int, _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        return InttRange(self.start, stop, self.step)[start::step]

    def retrieve_contains(self, incisor: int, /) -> int:
        if incisor >= 0:
            return _nth(self, incisor)
        raise ValueError(incisor)

    def __iter__(self, /):
        return self._iterfn()

    def __str__(self, /):
        return f"{self.start}::{self.step}"


class InttSpace(_Sliceable):

    def retrieve_contains_(self, incisor: int, /) -> int:
        return incisor

    def slice_incise_open(self, incisor: (int, type(None), _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        return InttCount(start, step)

    def slice_incise_closed(self, incisor: (_OPINT, int, _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        return InttRange(start, stop, step)


class Intt(metaclass=_Bythos):

    chora = InttSpace()

    @classmethod
    def incise(cls, chora, /):
        return InttIncision(cls, chora)

    @classmethod
    def retrieve(cls, index, /):
        return index

    @classmethod
    def __class_call__(cls, arg, /):
        return int(arg)


class InttIncision(_Incision):

    def __iter__(self, /):
        return iter(self.chora)

    @property
    def __call__(self, /):
        return self.incised.__class_call__


###############################################################################
###############################################################################
