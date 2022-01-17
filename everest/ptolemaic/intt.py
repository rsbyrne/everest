###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.utilities import caching as _caching
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    ChainIncisable as _ChainIncisable,
    )

from everest.ptolemaic import thing as _thing
from everest.ptolemaic.chora import (
    Sliceable as _Sliceable, Null as _Null
    )
from everest.ptolemaic.schema import Schema as _Schema
from everest.ptolemaic import tuuple as _tuuple


def _nth(iterable, n):
    try:
        return next(_itertools.islice(iterable, n, None))
    except StopIteration:
        raise IndexError(n)


_OPINT = (type(None), int)


class InttLike(_thing.ThingLike):
    ...


class InttGen(InttLike, _thing.ThingGen,):
    ...


class InttVar(InttLike, _thing.ThingVar):
    _default = 0


class InttSpace(_thing.ThingSpace):

    def __contains__(self, arg, /) -> bool:
        return isinstance(arg, int)

    __incise_generic__ = property(InttGen)
    __incise_variable__ = property(InttVar)


class _Intt_(InttSpace, _thing._Thing_):

    class Choret(_Sliceable):

        def handle_tuple(self, incisor: tuple, /, *, caller):
            if all(val in self.bound for val in incisor):
                return _IncisionProtocol.RETRIEVE(caller)(incisor)
            return _IncisionProtocol.SLYCE(
                Grid(len(incisor))
                )

        def retrieve_contains(self, incisor: int, /):
            raise incisor

        def slyce_inttspace(self, incisor: InttSpace, /):
            return incisor

#         def slyce_tuuple(self, incisor: _tuuple.TuupleMeta, /):
#             return Cell

        def slyce_depth(self, incisor: _tuuple.NTuuples, /):
            return Grid(incisor.n)

        def slice_slyce_open(self, incisor: (int, type(None), _OPINT), /):
            start, step = incisor.start, incisor.step
            if step is None:
                return InttCount(start)
            return InttCount(start, step)

        def slice_slyce_limit(self, incisor: (type(None), int, type(None)), /):
            return InttLimit(incisor.stop)

        def slice_slyce_closed(self, incisor: (int, int, _OPINT), /):
            start, stop, step = incisor.start, incisor.stop, incisor.step
            if step is None:
                return InttRange(start, stop)
            return InttRange(start, stop, step)


class InttMeta(_thing.ThingMeta):

    __incision_manager__ = _Intt_()


InttSpace.register(InttMeta)


class Intt(_thing.Thing, metaclass=InttMeta):

    @classmethod
    def __class_get_incision_manager__(cls, /):
        return _Intt_(cls)

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, int)

    @classmethod
    def __class_call__(cls, arg, /):
        return int(arg)


class InttLimit(InttSpace, _IncisionHandler, metaclass=_Schema):

    stop: Intt

    class Choret(_Sliceable):

        def slice_slyce_close(self, incisor: (int, _OPINT, _OPINT), /):
            start, stop, step = incisor.start, incisor.stop, incisor.step
            pstop = self.bound.stop
            if stop is None:
                stop = pstop
            elif stop > pstop:
                raise ValueError
            if step is None:
                return InttRange(start, stop)
            return InttRange(start, stop, step)

        def slice_slyce_open(self, incisor: (type(None), int, type(None)), /):
            stop = incisor.stop
            if stop > self.bound.stop:
                raise ValueError
            return self.bound._ptolemaic_class__(stop)

    def __contains__(self, arg, /):
        if isinstance(arg, int):
            return arg < self.stop
        return False


class InttCount(InttSpace, _IncisionHandler, metaclass=_Schema):

    start: Intt
    step: Intt = 1

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        if bound.arguments['step'] < 1:
            raise ValueError
        return bound

    class Choret(_Sliceable):

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


class InttRange(InttSpace, _IncisionHandler, metaclass=_Schema):

    start: Intt
    stop: Intt
    step: Intt[1:] = 1

    _req_slots__ = ('_rangeobj',)

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        start, stop, step = bound.args
        if start > stop:
            raise ValueError
        return bound

    def __init__(self, /):
        super().__init__()
        self._rangeobj = range(self.start, self.stop, self.step)

    class Choret(_Sliceable):

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


class CellLike(_tuuple.TuupleLike):
    ...


class CellGen(CellLike, _tuuple.TuupleGen):
    ...


class CellVar(CellLike, _tuuple.TuupleVar):
    ...


class CellSpace(_tuuple.TuupleSpace):

    def __contains__(self, arg, /) -> bool:
        if super().__contains__(arg):
            return all(val in Intt for val in arg)
        return False

    __incise_generic__ = property(CellGen)
    __incise_variable__ = property(CellVar)


class _Cell_(CellSpace, _tuuple._Tuuple_):

    class Choret:

        def retrieve_contains(self, incisor: tuple, /):
            return incisor

    def __incise_retrieve__(self, incisor, /):
        if incisor in self:
            return incisor
        raise ValueError(incisor)


class CellMeta(_tuuple.TuupleMeta):

    __incision_manager__ = _Cell_()


CellSpace.register(CellMeta)


class Cell(_tuuple.Tuuple, metaclass=CellMeta):
    ...


class Grid(CellSpace, _ChainIncisable, metaclass=_Schema):

    depth: Intt[0:]

    def __init__(self, /):
        super().__init__()
        self.dimensions = _tuuple.Tuuple[self.depth][Intt]

    @property
    def __incision_manager__(self, /):
        return self.dimensions

    @property
    def __incise_slyce__(self, /):
        return SubGrid

    @property
    def __contains__(self, /):
        return self.__incision_manager__.__contains__


class SubGrid(CellSpace, _ChainIncisable, metaclass=_Sprite):

    dimensions: _tuuple.TuPlex

    @property
    def __incision_manager__(self, /):
        return self._tuplex

    @property
    def __incise_slyce__(self, /):
        return self._ptolemaic_class__


# class CellOid(_tuuple.TuuplOid):

#     __incise_generic__ = property(CellGen)
#     __incise_variable__ = property(CellVar)


###############################################################################
###############################################################################
