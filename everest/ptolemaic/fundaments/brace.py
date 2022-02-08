###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from everest.incision import IncisionProtocol as _IncisionProtocol
from everest.utilities import pretty as _pretty

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.armature import (
    ArmatureProtocol as _ArmatureProtocol,
    Brace as _Brace,
    )
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Multi as _Multi,
    Sampleable as _Sampleable,
    )

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament


class Length(metaclass=_Sprite):

    n: int = 0


class Brace(_Fundament, _Brace, metaclass=_Bythos):


    SubmemberType = _Fundament

    @classmethod
    def __class_init__(cls, /):
        try:
            owner = cls.owner
        except AttributeError:
            pass
        else:
            cls.SubmemberType = owner
        super().__class_init__()
        cls._add_mroclass('SymForm', (cls.Slyce,))
        cls._add_mroclass('AsymForm', (cls.Slyce,))
        with (Slyce := cls.Slyce).mutable:
            Slyce.SubmemberType = cls.SubmemberType


    @classmethod
    def make_class_incision_manager(cls, /):
        return cls.Space(cls.SubmemberType)


    class Slyce(metaclass=_Essence):

        @property
        def SymForm(self, /):
            return self.MemberType.SymForm

        @property
        def AsymForm(self, /):
            return self.MemberType.AsymForm

        def validate_contents(self, arg, /):
            try:
                it = iter(arg)
            except TypeError:
                return False
            return all(isinstance(subarg, self.SubmemberType) for subarg in it)

        def __incise_contains__(self, arg, /):
            if super().__incise_contains__(arg):
                return self.validate_contents(arg)
            return False

        def __call__(self, arg, /):
            if not self.validate_contents(arg):
                raise ValueError(arg)
            return _IncisionProtocol.RETRIEVE(self)(arg)


    class SymForm(_Chora, metaclass=_Sprite):

        chora: _Chora
        labels: (tuple, int)

        @classmethod
        def __class_call__(cls, chora, labels):
            if not cls.SubmemberType.__includes__(chora):
                raise ValueError(chora)
            if isinstance(labels, int):
                labels = tuple(range(labels))
            typ = _ArmatureProtocol.BRACE(chora, cls.MemberType).SymForm
            if typ is cls:
                return super().__class_call__(chora, labels)
            return typ(chora, labels)

        @property
        def choras(self, /):
            return tuple(_itertools.repeat(self.chora, self.depth))

        @property
        def depth(self, /):
            return len(self.labels)

        def keys(self, /):
            return self.labels

        def values(self, /):
            return self.choras

        def __init__(self, /):
            super().__init__()
            if not self.SubmemberType.__includes__(self.chora):
                raise TypeError(self.chora, type(self.chora))

        __choret__ = _Multi

        @property
        def validate_contents(self, /):
            return _IncisionProtocol.CONTAINS(self.__incision_manager__)


    class AsymForm(_Chora, metaclass=_Sprite):

        choras: tuple
        labels: tuple = None

        @classmethod
        def __class_call__(cls, choras, labels=None):
            if labels is None:
                if isinstance(choras, _collabc.Mapping):
                    choras, labels = tuple(choras.values()), tuple(choras)
                else:
                    labels = tuple(range(len(choras)))
            if not all(map(cls.SubmemberType.__includes__, choras)):
                raise ValueError(choras)
            if len(typset := set(
                    _ArmatureProtocol.BRACE(chora, cls.MemberType).AsymForm
                    for chora in choras
                    )) == 1:
                typ = typset.pop()
                if typ is not cls:
                    return typ(choras, labels)
            return super().__class_call__(choras, labels)

        @property
        def depth(self, /):
            return len(self.choras)

        def __init__(self, /):
            super().__init__()
            if not all(map(self.SubmemberType.__includes__, self.choras)):
                raise TypeError(self.choras)

        __choret__ = _Multi

        @property
        def depth(self, /):
            return len(self.choras)

        def keys(self, /):
            return self.labels

        def values(self, /):
            return self.choras

        def asdict(self, /):
            return dict(zip(self.keys(), self.values()))

        @property
        def validate_contents(self, /):
            return _IncisionProtocol.CONTAINS(self.__incision_manager__)

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self.rootrepr
            _pretty.pretty_dict(self.asdict(), p, cycle, root=root)


    class Space(metaclass=_Sprite):

        chora: _Chora

        class __choret__(_Sampleable):

            @property
            def chora(self, /):
                return self.bound.chora

            def handle_tuple(self, incisor: tuple, /, *, caller):
                nspace = self.slyce_n(Length(len(incisor)))
                return _IncisionProtocol.INCISE(nspace)(incisor, caller=caller)

            def slyce_dict(self, incisor: dict, /):
                symform = self.bound.SymForm(self.chora, tuple(incisor))
                return symform[tuple(incisor.values())]

            def sample_slyce_chora(self, incisor: _Chora, /):
                if not self.bound.SubmemberType.__includes__(incisor):
                    raise TypeError(self.bound, type(incisor))
                try:
                    return _ArmatureProtocol.BRACE(incisor)
                except AttributeError:
                    return self.bound._ptolemaic_class__(incisor)

            def slyce_n(self, incisor: Length, /):
                return self.bound.SymForm(self.chora, incisor.n)

        def __incise_trivial__(self, /):
            if self.chora is self.SubmemberType:
                return self.MemberType
            return self


_ = Brace.register(tuple)


###############################################################################
###############################################################################
