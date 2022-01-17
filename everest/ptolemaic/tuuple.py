###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.utilities import caching as _caching
from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic import thing as _thing, intt as _intt
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Basic as _Basic,
    Degenerate as _Degenerate,
    Degenerator as _Degenerator,
    Null as _Null,
    )


class TuupleLike(_thing.ThingLike):
    ...


class TuupleGen(TuupleLike, _thing.ThingGen):
    ...


class TuupleVar(TuupleLike, _thing.ThingVar):
    ...


class TuupleSpace(_thing.ThingSpace):

    def __contains__(self, arg, /) -> bool:
        return isinstance(arg, tuple)

    __incise_generic__ = property(TuupleGen)
    __incise_variable__ = property(TuupleVar)


class _Tuuple_(TuupleSpace, _thing._Thing_):

    class Choret:

        def retrieve_contains(self, incisor: tuple, /):
            return incisor

        def slyce_length(self, incisor: int, /):
            return NTuuples(incisor)

        def slyce_chora(self, incisor: _Chora, /):
            return TuuplesOf(incisor)


class TuupleMeta(_thing.ThingMeta):

    __incision_manager__ = _Tuuple_()


TuupleSpace.register(TuupleMeta)


class Tuuple(_thing.Thing, metaclass=TuupleMeta):

    @classmethod
    def tuplex(self, /, *args):
        return TuPlex(args)


class TuuplesOf(_Chora, TuupleSpace, metaclass=_Sprite):

    typ: _Chora

    class Choret(_Basic):

        @property
        def typ(self, /):
            return self.bound.typ

        def retrieve_tuple(self, incisor: tuple, /):
            return incisor

        def slyce_length(self, incisor: int, /):
            return TuPlex(_itertools.repeat(self.typ, incisor))

    def __contains__(self, arg, /) -> bool:
        if super().__contains__(arg):
            return all(val in self.typ for val in arg)
        return False


class NTuuples(_Chora, TuupleSpace, metaclass=_Sprite):

    n: int

    class Choret(_Basic):

        @property
        def n(self, /):
            return self.bound.n

        def retrieve_tuple(self, incisor: tuple, /):
            return incisor

        def slyce_chora(self, incisor: _Chora, /):
            return TuPlex(_itertools.repeat(incisor, self.n))

    def __incise_retrieve__(self, incisor, /):
        if incisor in self:
            return incisor
        raise ValueError(len(incisor))

    def __contains__(self, arg, /) -> bool:
        if super().__contains__(arg):
            return len(arg) == self.n
        return False


class TuPlex(_Chora, metaclass=_Sprite):

    choras: tuple

    def __new__(cls, /, arg):
        return super().__new__(cls, tuple(arg))

    class Choret(_Basic):

    #     BOUNDREQS = ('choras',)

        @property
        def choras(self, /):
            return self.bound.choras

        @property
        def __call__(self, /):
            return self.bound._ptolemaic_class__

        @property
        def depth(self, /):
            return len(self.choras)

        @property
        @_caching.soft_cache()
        def active(self, /):
            return tuple(
                not isinstance(cho, _Degenerate) for cho in self.choras
                )

        @property
        @_caching.soft_cache()
        def activechoras(self, /):
            return tuple(_itertools.compress(self.choras, self.active))

        @property
        def activedepth(self, /):
            return len(self.activechoras)

        def yield_tuple_multiincise(self, /, *incisors):
            ninc, ncho = len(incisors), self.activedepth
            nell = incisors.count(...)
            if nell:
                ninc -= nell
                if ninc % nell:
                    raise ValueError("Cannot resolve incision ellipses.")
                ellreps = (ncho - ninc) // nell
            chorait = iter(self.choras)
            try:
                for incisor in incisors:
                    if incisor is ...:
                        count = 0
                        while count < ellreps:
                            chora = next(chorait)
                            if not isinstance(chora, _Degenerate):
                                count += 1
                            yield chora
                        continue
                    while True:
                        chora = next(chorait)
                        if isinstance(chora, _Degenerate):
                            yield chora
                            continue
                        yield _Degenerator(chora)[incisor]
                        break
            except StopIteration:
    #             raise ValueError("Too many incisors in tuple incision.")
                pass
            yield from chorait

        def handle_tuple(self, incisor: tuple, /, *, caller):
            '''Captures the special behaviour implied by `self[a,b,...]`'''
            choras = tuple(self.yield_tuple_multiincise(*incisor))
            if all(isinstance(cho, _Degenerate) for cho in choras):
                incisor = tuple(cho.value for cho in choras)
                return _IncisionProtocol.RETRIEVE(caller)(incisor)
            return _IncisionProtocol.SLYCE(caller)(self(choras))

    __incise_generic__ = property(TuupleGen)
    __incise_variable__ = property(TuupleVar)

    def depth(self, /):
        return len(self.choras)

    def __contains__(self, arg: tuple, /):
        for val, chora in zip(arg, self.choras):
            if val not in chora:
                return False
        return True

    def __call__(self, arg, /):
        raise NotImplementedError


###############################################################################
###############################################################################
