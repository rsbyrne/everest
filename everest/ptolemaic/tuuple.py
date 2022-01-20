###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from everest.utilities import caching as _caching
from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic import thing as _thing
from everest.ptolemaic import armature as _armature
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Multi as _Multi,
    Basic as _Basic,
    Degenerate as _Degenerate,
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
    contentspace = _thing.Thing

    __incise_generic__ = property(TuupleGen)
    __incise_variable__ = property(TuupleVar)

    @property
    def SymForm(self, /):
        return SymBrace

    @property
    def AsymForm(self, /):
        return AsymBrace

    def __contains__(self, arg, /) -> bool:
        if super().__contains__(arg):
            return all(map(self.contentspace.__includes__, arg))
        return False


class SymBrace(_Chora, TuupleSpace, metaclass=_Sprite):

    chora: _Chora = _thing.Thing
    keys: tuple = None

    @classmethod
    def __class_call__(cls, chora, keys):
        if not cls.contentspace.__includes__(chora):
            raise ValueError(chora)
        if isinstance(keys, int):
            keys = tuple(range(keys))
        return super().__class_call__(chora, keys)

    @property
    def depth(self, /):
        return len(self.keys)

    def __init__(self, /):
        super().__init__()
        if not self.contentspace.__includes__(self.chora):
            raise TypeError(self.chora, type(self.chora))

    @property
    def choras(self, /):
        return tuple(_itertools.repeat(self.chora, self.depth))

    __incision_manager__ = _Multi

    @property
    def __contains__(self, /):
        return self.__incision_manager__.__contains__


class AsymBrace(_Chora, TuupleSpace, metaclass=_Sprite):

    choras: tuple
    keys: tuple = None

    @classmethod
    def __class_call__(cls, choras, keys=None):
        if keys is None:
            if isinstance(choras, _collabc.Mapping):
                choras, keys = tuple(choras.values()), tuple(choras)
            else:
                keys = tuple(range(len(choras)))
        if not all(map(cls.contentspace.__includes__, choras)):
            raise ValueError(choras)
        return super().__class_call__(choras, keys)

    @property
    def depth(self, /):
        return len(self.choras)

    def __init__(self, /):
        super().__init__()
        if not all(map(self.contentspace.__includes__, self.choras)):
            raise TypeError(self.choras)

    __incision_manager__ = _Multi

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
            if not all(map(self.bound.contentspace.__includes__, incisor)):
                return _IncisionProtocol.FAIL(caller)(incisor)
            nspace = self.slyce_n(len(incisor))
            return _IncisionProtocol.INCISE(nspace)(incisor, caller=caller)

        def slyce_chora(self, incisor: _Chora = _thing.Thing, /):
            if not self.bound.contentspace.__includes__(incisor):
                raise TypeError(self.bound, type(incisor))
            try:
                return _armature.ArmatureProtocol.BRACE(incisor)
            except AttributeError:
                return self.bound._ptolemaic_class__(incisor)

        def slyce_n(self, incisor: int, /):
            return self.bound.SymForm(self.chora, incisor)

    def __contains__(self, arg, /) -> bool:
        if super().__contains__(arg):
            return all(val in self.chora for val in arg)
        return False

    @property
    def __incise_trivial__(self, /):
        return Tuuple if self.chora is _thing.Thing else self


class TuupleMeta(_thing.ThingMeta):

    @property
    def SymForm(cls, /):
        return cls.__class_incision_manager__.SymBrace

    @property
    def AsymForm(cls, /):
        return cls.__class_incision_manager__.AsymBrace


TuupleSpace.register(TuupleMeta)


class Tuuple(_thing.Thing, metaclass=TuupleMeta):

    __class_incision_manager__ = Brace()


class _TuupleNull_(_thing._ThingNull_, TuupleSpace):

    @property
    def __incise_trivial__(self, /):
        return TuupleNull


class TuupleNull(Tuuple):

    __class_incision_manager__ = _TuupleNull_()


###############################################################################
###############################################################################
