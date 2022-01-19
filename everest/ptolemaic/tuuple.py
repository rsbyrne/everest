###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.utilities import caching as _caching
from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic import thing as _thing
from everest.ptolemaic import armature as _armature
from everest.ptolemaic.chora import (
    Chora as _Chora,
    MultiTuple as _MultiTuple,
    Basic as _Basic,
    Degenerate as _Degenerate,
    Degenerator as _Degenerator,
    Null as _Null,
    )


class TuupleLike(_thing.ThingLike):
    ...


TuupleLike.register(tuple)


class TuupleGen(TuupleLike, _thing.ThingGen):
    ...


class TuupleVar(TuupleLike, _thing.ThingVar):
    ...


class TuupleSpace(_thing.ThingSpace):

    MemberType = TuupleLike
    ContentSpace = _thing.ThingSpace

    __incise_generic__ = property(TuupleGen)
    __incise_variable__ = property(TuupleVar)

    @property
    def IsoForm(self, /):
        return IsoBrace

    @property
    def AnisoForm(self, /):
        return AnisoBrace


class IsoBrace(_Chora, TuupleSpace, metaclass=_Sprite):

    chora: _Chora = _thing.Thing
    depth: int = 0

    def __init__(self, /):
        super().__init__()
        if not isinstance(self.chora, self.ContentSpace):
            raise TypeError(self.chora, type(self.chora))

    @property
    def choras(self, /):
        return tuple(_itertools.repeat(self.chora, self.depth))

    __incision_manager__ = _MultiTuple

    @property
    def __contains__(self, /):
        return self.__incision_manager__.__contains__


class AnisoBrace(_Chora, TuupleSpace, metaclass=_Sprite):

    choras: tuple

    def __init__(self, /):
        super().__init__()
        if not all(isinstance(cho, self.ContentSpace) for cho in self.choras):
            raise TypeError(self.choras)

    __incision_manager__ = _MultiTuple

    @property
    def depth(self, /):
        return len(self.choras)

    @property
    def __contains__(self, /):
        return self.__incision_manager__.__contains__


class Brace(_Chora, TuupleSpace, metaclass=_Sprite):

    chora: _Chora = _thing.Thing

    class __incision_manager__(_Basic):

        @property
        def chora(self, /):
            return self.bound.chora

        def handle_tuple(self, incisor: tuple, /, *, caller):
            if not all(
                    isinstance(arg, self.bound.ContentSpace)
                    for arg in incisor
                    ):
                raise ValueError(incisor)
            nspace = self.slyce_n(len(incisor))
            return _IncisionProtocol.INCISE(nspace)(incisor, caller=caller)

        def slyce_chora(self, incisor: _Chora = _thing.Thing, /):
            if not isinstance(incisor, self.bound.ContentSpace):
                raise TypeError(type(incisor))
            try:
                return _armature.ArmatureProtocol.BRACE(incisor)
            except AttributeError:
                return self.bound._ptolemaic_class__(incisor)

        def slyce_n(self, incisor: int, /):
            return self.bound.IsoForm(self.chora, incisor)

    def __contains__(self, arg, /) -> bool:
        if super().__contains__(arg):
            return all(val in self.chora for val in arg)
        return False


class TuupleMeta(_thing.ThingMeta):

    __class_incision_manager__ = Brace()


TuupleSpace.register(TuupleMeta)


class Tuuple(_thing.Thing, metaclass=TuupleMeta):
    ...


###############################################################################
###############################################################################
