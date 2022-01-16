###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.utilities import caching as _caching
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    )

from everest.ptolemaic import thing as _thing
from everest.ptolemaic.chora import (
    Sliceable as _Sliceable,
    )
from everest.ptolemaic.schema import Schema as _Schema


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


_OPINT = (type(None), int)


class InttLike(_thing.ThingLike):
    ...


class InttElement(_thing.ThingElement, InttLike):
    ...


class InttGeneric(_thing.ThingGeneric, InttElement):
    ...


class InttVar(_thing.ThingVar, InttElement):
    _default = 0


class InttSpace(_Sliceable, _thing.ThingSpace, InttLike):

    @property
    def __incise_generic__(self, /):
        return InttGeneric(self.bound)

    @property
    def __incise_variable__(self, /):
        return InttVar(self.bound)

    def retrieve_contains(self, incisor: int, /):
        return incisor

    def slice_slyce_open(self, incisor: (int, type(None), _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        return InttCount(start, step)

    def slice_slyce_closed(self, incisor: (_OPINT, int, _OPINT), /):
        start, stop, step = incisor.start, incisor.stop, incisor.step
        return InttRange(start, stop, step)


class Intt(InttLike, _thing.Thing):

    @classmethod
    def __class_get_incision_manager__(cls, /):
        return InttSpace(cls)

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, int)


class InttCount(InttLike, _IncisionHandler, metaclass=_Schema):

    start: Intt
    step: Intt

    __incise_generic__ = property(InttGeneric)
    __incise_variable__ = property(InttVar)

    class Choret(_Sliceable):

        BOUNDREQS = ('start', 'step')

        def handle_intlike(self, incisor: InttLike, /, *, caller):
            if isinstance(incisor, InttRange):
                incisor = self.slice_slyce_closed(incisor.slc)
            elif isinstance(incisor, InttCount):
                incisor = self.slice_slyce_open(incisor.slc)
            elif incisor is Intt:
                return _IncisionProtocol.TRIVIAL(caller)()
            else:
                raise TypeError(type(incisor))
            return _IncisionProtocol.SLYCE(caller)(incisor)

        def slice_slyce_open(self, incisor: (int, type(None), _OPINT), /):
            start, stop, step = incisor.start, incisor.stop, incisor.step
            pstart, pstep = self.bound.start, self.bound.step
            if start is not None:
                if start < 0:
                    raise ValueError(start)
                pstart += int(start)
            if step is not None:
                if step < 0:
                    raise ValueError(step)
                pstep *= int(step)
            return InttCount(pstart, pstep)

        def slice_slyce_closed(self, incisor: (_OPINT, int, _OPINT), /):
            istart, istop, istep = incisor.start, incisor.stop, incisor.step
            start, step = self.bound.start, self.bound.step
            if istart is not None:
                start += istart
            stop = start + istop
            if istep is not None:
                step *= istep
            return InttRange(start, stop, step)

        def retrieve_int(self, incisor: int, /) -> int:
            if incisor >= 0:
                return _nth(self.bound, incisor)
            raise ValueError(incisor)

    @classmethod
    def parameterise(cls, cache, /, *args):
        bound = super().parameterise(cache, *args)
        start, step = bound.args
        if start is None:
            bound.arguments['start'] = 0
        if step is None:
            bound.arguments['step'] = 1
        return bound

    @property
    @_caching.soft_cache()
    def slc(self, /):
        return slice(self.start, None, self.step)

    def __iter__(self, /):
        return _itertools.count(self.start, self.step)

    def __contains__(self, arg, /):
        if not isinstance(arg, int):
            return False
        if arg < self.start:
            return False
        return not (arg - self.start) % self.step

    def __str__(self, /):
        return f"{self.start}::{self.step}"


class InttRange(InttLike, _IncisionHandler, metaclass=_Schema):

    start: Intt
    stop: Intt
    step: Intt[1:] = 1

    _req_slots__ = ('_rangeobj',)

    __incise_generic__ = property(InttGeneric)
    __incise_variable__ = property(InttVar)

    class Choret(_Sliceable):

        BOUNDREQS = ('start', 'stop', 'step')

        def handle_intlike(self, incisor: InttLike, /, *, caller):
            if isinstance(incisor, InttRange):
                slc = incisor.slc
            elif isinstance(incisor, InttCount):
                slc = slice(incisor.start, self.bound.stop, incisor.bound.step)
            elif incisor is Intt:
                return _IncisionProtocol.TRIVIAL(caller)()
            else:
                raise TypeError(type(incisor))
            incisor = self.slice_slyce_nontrivial(slc)
            return _IncisionProtocol.SLYCE(caller)(incisor)

        def handle_int(self, incisor: int, /, *, caller):
            try:
                out = self.bound._rangeobj[incisor]
            except IndexError:
                return _IncisionProtocol.FAIL(caller)(incisor)
            return _IncisionProtocol.RETRIEVE(caller)(out)

        def slice_slyce_nontrivial(self, incisor: (_OPINT, _OPINT, _OPINT), /):
            start, stop, step = incisor.start, incisor.stop, incisor.step
            nrang = self.bound._rangeobj[start:stop:step]
            return InttRange(nrang.start, nrang.stop, nrang.step)

    @classmethod
    def parameterise(cls, cache, arg0, /, *argn):
        if isinstance(arg0, slice):
            if argn:
                raise cls.paramexc("Cannot pass both slc and args.")
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
        self._rangeobj = range(self.start, self.stop, self.step)

    @property
    @_caching.soft_cache()
    def slc(self, /):
        return slice(self.start, self.stop, self.step)

    def __iter__(self, /):
        return iter(self._rangeobj)

    def __len__(self, /):
        return len(self._rangeobj)

    @property
    def __contains__(self, /):
        return self._rangeobj.__contains__

    def __reversed__(self, /):
        return self[::-1]


###############################################################################
###############################################################################
