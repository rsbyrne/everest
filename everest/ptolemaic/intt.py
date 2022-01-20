###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.utilities import caching as _caching
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic import thing as _thing
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Sampleable as _Sampleable,
    Degenerate as _Degenerate,
    TrivialException as _TrivialException,
    )
from everest.ptolemaic.schema import Schema as _Schema
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic import tuuple as _tuuple


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


_OPINT = (type(None), int)


class InttLike(_thing.ThingLike):
    ...


InttLike.register(int)


class InttGen(InttLike, _thing.ThingGen,):
    ...


class InttVar(InttLike, _thing.ThingVar):
    _default = 0


class InttSpace(_thing.ThingSpace):

    MemberType = InttLike

    __incise_generic__ = property(InttGen)
    __incise_variable__ = property(InttVar)

    @property
    def __armature_brace__(self, /):
        return Cell

#     @property
#     def __incise_degenerate__(self, /):
#         return InttDegenerate


# class InttDegenerate(InttSpace, _Degenerate):
#     ...


class _Intt_(InttSpace, _thing._Thing_):

    class __incision_manager__(_Sampleable):

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

    @property
    def __incise_trivial__(self, /):
        return Intt


class InttMeta(_thing.ThingMeta):

    ...


InttSpace.register(InttMeta)


class Intt(_thing.Thing, metaclass=InttMeta):

    __class_incision_manager__ = _Intt_()


class _InttNull_(_thing._ThingNull_, _Intt_):

    @property
    def __incise_trivial__(self, /):
        return InttNull


class InttNull(Intt):

    __class_incision_manager__ = _InttNull_()


class InttOpen(_Chora, InttSpace, metaclass=_Schema):

    lower: Intt
    step: Intt = 1

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        if bound.arguments['step'] < 1:
            raise ValueError
        return bound

    class __incision_manager__(_Sampleable):

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
            lower, upper = incisor
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

    def __iter__(self, /):
        return _itertools.count(self.lower, self.step)

    def __contains__(self, arg, /):
        if not super().__contains__(arg):
            return False
        if arg < self.lower:
            return False
        return not (arg - self.lower) % self.step

    def __includes__(self, arg, /):
        raise NotImplementedError


class InttLimit(_Chora, InttSpace, metaclass=_Schema):

    upper: Intt

    class __incision_manager__(_Sampleable):

        def retrieve_int(self, incisor: int, /):
            if incisor < 0:
                return self.bound.upper + incisor
            raise IndexError('foo')

        def bounds_slyce_open(self, incisor: (int, type(None)), /):
            lower, upper = incisor.lower, self.bound.upper
            if lower >= 0:
                raise IndexError
            return InttClosed(lower, upper)

        def bounds_slyce_limit(self, incisor: (type(None), int), /):
            upper = incisor.upper
            if upper >= 0:
                raise IndexError
            return self.bound._ptolemaic_class__(self.bound.upper + upper)

        def bounds_slyce_closed(self, incisor: (int, int), /):
            lower, upper = incisor
            if upper >= 0:
                raise IndexError
            upper = self.bound.upper + upper
            if upper <= lower:
                return InttNull
            return InttClosed(lower, upper)

    def __contains__(self, arg, /):
        if not super().__contains__(arg):
            return False
        return arg < self.upper

    def __includes__(self, arg, /):
        raise NotImplementedError


class InttClosed(_Chora, InttSpace, metaclass=_Schema):

    lower: Intt
    upper: Intt
    step: Intt[1:] = 1

    _req_slots__ = ('_rangeobj',)

    def __init__(self, /):
        super().__init__()
        self._rangeobj = range(self.lower, self.upper, self.step)

    class __incision_manager__(_Sampleable):

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

    def __iter__(self, /):
        return iter(self._rangeobj)

    def __len__(self, /):
        return len(self._rangeobj)

    @property
    def __contains__(self, /):
        return self._rangeobj.__contains__

    def __includes__(self, arg, /):
        raise NotImplementedError


class CellLike(_tuuple.TuupleLike):
    ...


class CellGen(CellLike, _tuuple.TuupleGen):
    ...


class CellVar(CellLike, _tuuple.TuupleVar):
    ...


class CellSpace(_tuuple.TuupleSpace):

    contentspace = Intt

    __incise_generic__ = property(CellGen)
    __incise_variable__ = property(CellVar)

    @property
    def SymForm(self, /):
        return SymGrid

    @property
    def AsymForm(self, /):
        return AsymGrid


class SymGrid(CellSpace, _tuuple.SymBrace):
    ...


class AsymGrid(CellSpace, _tuuple.AsymBrace):
    ...


class Grid(CellSpace, _tuuple.Brace):

    chora: _Chora = Intt

    @property
    def __incise_trivial__(self, /):
        return Cell if self.chora is Intt else self


class CellMeta(_tuuple.TuupleMeta):

    __class_incision_manager__ = Grid()


CellSpace.register(CellMeta)


class Cell(_tuuple.Tuuple, metaclass=CellMeta):
    ...


###############################################################################
###############################################################################
