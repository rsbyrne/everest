###############################################################################
''''''
###############################################################################


import itertools as _itertools
import typing as _typing

from everest.utilities import caching as _caching

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.eidos import Eidos as _Eidos
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


class InttChora(_Sliceable, metaclass=_Eidos):
    ...


class InttRange(InttChora):

    _req_slots__ = ('_iterfn', '_lenfn', '_rangeobj', '_tupobj',)

    start: _typing.Optional[int]
    stop: int
    step: _typing.Optional[int] = 1

    @classmethod
    def parameterise(cls, cache, arg0, /, *argn):
        if isinstance(arg0, slice):
            if argn:
                raise Exception("Cannot pass both slc and args.")
            slc = arg0
        else:
            slc = slice(arg0, *argn) 
        bound = super().parameterise(cache, slc.start, slc.stop, slc.step)
        start, stop, step = bound.args
        bound.arguments.update(
            start=(0 if start is None else int(start)),
            stop=int(stop),
            step=(1 if step is None else int(step)),
            )
        return bound

    def __init__(self, /):
        super().__init__()
        rangeobj = self._rangeobj = range(self.start, self.stop, self.step)
        tupobj = self._tupobj = tuple(rangeobj)
        self._iterfn = tupobj.__iter__
        self._lenfn = tupobj.__len__

    @property
    @_caching.soft_cache()
    def slc(self, /):
        return slice(self.start, self.stop, self.step)

    def __iter__(self, /):
        return self._iterfn()

    def __len__(self, /):
        return self._lenfn()

    def __reversed__(self, /):
        return self[::-1]

    def handle_inttchora(self, incisor: InttChora, /, *, caller):
        if isinstance(incisor, InttRange):
            slc = incisor.slc
        elif isinstance(incisor, InttCount):
            slc = slice(incisor.start, self.stop, incisor.step)
        else:
            raise TypeError(type(incisor))
        incisor = self.slice_incise_nontrivial(slc)
        return caller.incise(incisor)

    def slice_incise_nontrivial(self, incisor: (_OPINT, _OPINT, _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        nrang = self._rangeobj[start:stop:step]
        return InttRange(nrang.start, nrang.stop, nrang.step)

    def retrieve_contains(self, incisor: int, /) -> int:
        return self._tupobj[incisor]

    def __str__(self, /):
        return ':'.join(map(str, self.args))


class InttCount(InttChora):

    _req_slots__ = ('_iterfn',)

    start: int
    step: int

    @classmethod
    def parameterise(cls, cache, /, *args):
        bound = super().parameterise(cache, *args)
        start, step = bound.args
        if start is None:
            bound.arguments['start'] = 0
        if step is None:
            bound.arguments['step'] = 1
        return bound

    def __init__(self, /):
        super().__init__()
        self._iterfn = _itertools.count(self.start, self.step).__iter__

    @property
    @_caching.soft_cache()
    def slc(self, /):
        return slice(self.start, None, self.step)

#     def __instancecheck__(self, val: int, /):
#         start, step = self.start, self.step
#         return val >= start and not (val - start) % step

    def handle_inttchora(self, incisor: InttChora, /, *, caller):
        if isinstance(incisor, InttRange):
            incisor = self.slice_incise_closed(incisor.slc)
        elif isinstance(incisor, InttCount):
            incisor = self.slice_incise_open(incisor.slc)
        else:
            raise TypeError(type(incisor))
        return caller.incise(incisor)

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

    def slice_incise_closed(self, incisor: (_OPINT, int, _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        selfstart, selfstep = self.start, self.step
        return InttRange(selfstart+start, selfstart+stop, selfstep*step)

    def retrieve_contains(self, incisor: int, /) -> int:
        if incisor >= 0:
            return _nth(self, incisor)
        raise ValueError(incisor)

    def __iter__(self, /):
        return self._iterfn()

    def __str__(self, /):
        return f"{self.start}::{self.step}"


class _InttSpace_(InttChora):

    def retrieve_contains_(self, incisor: int, /) -> int:
        return incisor

    def slice_incise_open(self, incisor: (int, type(None), _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        return InttCount(start, step)

    def slice_incise_closed(self, incisor: (_OPINT, int, _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        return InttRange(start, stop, step)


Intt = _InttSpace_()


# class Intt(metaclass=_Bythos):

#     chora = InttSpace()

#     @classmethod
#     def incise(cls, chora, /):
#         return InttIncision(cls, chora)

#     @classmethod
#     def retrieve(cls, index, /):
#         return index

#     @classmethod
#     def __class_call__(cls, arg, /):
#         return int(arg)


# class InttIncision(_Incision):

#     def __iter__(self, /):
#         return iter(self.chora)

#     @property
#     def __call__(self, /):
#         return self.incised.__class_call__


###############################################################################
###############################################################################
