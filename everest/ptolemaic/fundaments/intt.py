###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.schema import Schema as _Schema
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Sampleable as _Sampleable,
    TrivialException as _TrivialException,
    )

from everest.ptolemaic.fundaments.thing import Thing as _Thing


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


_OPINT = (type(None), int)


class Intt(_Thing):


    class Var(metaclass=_Essence):
        _default = 0


    class Space(metaclass=_Essence):

        class __choret__(metaclass=_Essence):

            def retrieve_contains(self, incisor: int, /):
                return incisor

            def bounds_slyce_open(self, incisor: (int, type(None))):
                return InttOpen(incisor.lower)

            def bounds_slyce_limit(self, incisor: (type(None), int)):
                return InttLimit(incisor.upper)

            def bounds_slyce_closed(self, incisor: (int, int)):
                lower, upper = incisor
                if upper <= lower:
                    return InttNull
                return InttClosed(lower, upper)


_ = Intt.register(int)


class InttOpen(_Chora, Intt.Oid, metaclass=_Schema):

    lower: Intt
    step: Intt = 1

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        if bound.arguments['step'] < 1:
            raise ValueError
        return bound

    class __choret__(_Sampleable):

        def retrieve_int(self, incisor: int, /):
            if incisor >= 0:
                return _nth(self.bound, incisor)
            raise IndexError

        def bounds_slyce_open(self, incisor: (int, type(None)), /):
            lower = incisor.lower
            if lower == 0:
                raise _TrivialException
            elif lower < 0:
                raise IndexError
            return self.bound._ptolemaic_class__(
                lower + self.bound.lower,
                self.bound.step,
                )

        def bounds_slyce_limit(self, incisor: (type(None), int), /):
            lower = self.bound.lower
            upper = incisor.upper
            if upper == 0:
                return InttNull
            elif upper < 0:
                raise IndexError
            return InttClosed(lower, lower + upper, self.bound.step)

        def bounds_slyce_closed(self, incisor: (int, int), /):
            lower, upper = incisor.lower, incisor.upper
            if upper <= lower:
                return InttNull
            if upper == 0:
                raise _TrivialException
            if upper < 0:
                raise IndexError
            oldlower = self.bound.lower
            lower = oldlower + lower
            upper = oldlower + upper
            return InttClosed(lower, upper, self.bound.step)

    def __incise_iter__(self, /):
        return _itertools.count(self.lower, self.step)

    def __incise_contains__(self, arg, /):
        if not super().__contains__(arg):
            return False
        if arg < self.lower:
            return False
        return not (arg - self.lower) % self.step

    def __incise_includes__(self, arg, /):
        raise NotImplementedError


class InttLimit(_Chora, Intt.Oid, metaclass=_Schema):

    upper: Intt

    class __choret__(_Sampleable):

        def retrieve_int(self, incisor: int, /):
            if incisor < 0:
                return self.bound.upper + incisor
            raise IndexError

        def bounds_slyce_open(self, incisor: (int, type(None)), /):
            lower, upper = incisor.lower, self.bound.upper
            if lower >= 0:
                raise IndexError
            lower = upper + lower
            return InttClosed(lower, upper)

        def bounds_slyce_limit(self, incisor: (type(None), int), /):
            upper = incisor.upper
            if upper >= 0:
                raise IndexError
            return self.bound._ptolemaic_class__(self.bound.upper + upper)

        def bounds_slyce_closed(self, incisor: (int, int), /):
            lower, upper = incisor.lower, incisor.upper
            if upper >= 0:
                raise IndexError
            upper = self.bound.upper + upper
            if upper <= lower:
                return InttNull
            return InttClosed(lower, upper)

    def __incise_contains__(self, arg, /):
        if not super().__contains__(arg):
            return False
        return arg < self.upper

    def __incise_includes__(self, arg, /):
        raise NotImplementedError


class InttClosed(_Chora, Intt.Oid, metaclass=_Schema):

    lower: Intt
    upper: Intt
    step: Intt[1:] = 1

    _req_slots__ = ('_rangeobj',)

    def __init__(self, /):
        super().__init__()
        self._rangeobj = range(self.lower, self.upper, self.step)

    class __choret__(_Sampleable):

        def retrieve_int(self, incisor: int, /):
            return self.bound._rangeobj[incisor]

        def bounds_handle_any(self, incisor: (_OPINT, _OPINT), /, *, caller):
            oldr = self.bound._rangeobj
            newr = oldr[slice(*incisor)]
            if len(newr) == 0:
                return _IncisionProtocol.SLYCE(caller)(InttNull)
            start, stop, step = newr.start, newr.stop, newr.step
            if (stop, stop, step) == (oldr.start, oldr.stop, oldr.step):
                return _IncisionProtocol.TRIVIAL(caller)
            return _IncisionProtocol.SLYCE(caller)(
                self.bound._ptolemaic_class__(start, stop, step)
                )

    def __incise_iter__(self, /):
        return iter(self._rangeobj)

    def __incise_length__(self, /):
        return len(self._rangeobj)

    @property
    def __incise_contains__(self, /):
        return self._rangeobj.__contains__

    def __incise_includes__(self, arg, /):
        raise NotImplementedError


###############################################################################
###############################################################################
