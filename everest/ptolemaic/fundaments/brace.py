###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from everest.incision import IncisionProtocol as _IncisionProtocol

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


class Brace(_Fundament, _Brace, metaclass=_Bythos):


#     SubmemberType = None

    @classmethod
    def __class_init__(cls, /):
        try:
            owner = cls.owner
        except AttributeError:
            owner = None
        cls.SubmemberType = owner
        super().__class_init__()
        cls._add_mroclass('SymForm', (cls.Oid,))
        cls._add_mroclass('AsymForm', (cls.Oid,))
        with (Oid := cls.Oid).mutable:
            Oid.SubmemberType = cls.SubmemberType


    @classmethod
    def make_class_incision_manager(cls, /):
        return cls.Space(cls.SubmemberType)


    class Oid(metaclass=_Essence):

        @property
        def __incise_retrieve__(self, /):
            return _IncisionProtocol.RETRIEVE(self.MemberType)

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
                raise ValueError
            return _IncisionProtocol.RETRIEVE(self)(arg)


    class SymForm(_Chora, metaclass=_Sprite):

        chora: _Chora
        keys: tuple = None

        @classmethod
        def __class_call__(cls, chora, keys):
            if not cls.SubmemberType.__includes__(chora):
                raise ValueError(chora)
            if isinstance(keys, int):
                keys = tuple(range(keys))
            typ = _ArmatureProtocol.BRACE(chora, cls.MemberType).SymForm
            if typ is cls:
                return super().__class_call__(chora, keys)
            return typ(chora, keys)

        @property
        def depth(self, /):
            return len(self.keys)

        def __init__(self, /):
            super().__init__()
            if not self.SubmemberType.__includes__(self.chora):
                raise TypeError(self.chora, type(self.chora))

        @property
        def choras(self, /):
            return tuple(_itertools.repeat(self.chora, self.depth))

        __choret__ = _Multi

        @property
        def validate_contents(self, /):
            return _IncisionProtocol.CONTAINS(self.incision_manager)


    class AsymForm(_Chora, metaclass=_Sprite):

        choras: tuple
        keys: tuple = None

        @classmethod
        def __class_call__(cls, choras, keys=None):
            if keys is None:
                if isinstance(choras, _collabc.Mapping):
                    choras, keys = tuple(choras.values()), tuple(choras)
                else:
                    keys = tuple(range(len(choras)))
            if not all(map(cls.SubmemberType.__includes__, choras)):
                raise ValueError(choras)
            if len(typset := set(
                    _ArmatureProtocol.BRACE(chora, cls.MemberType).AsymForm
                    for chora in choras
                    )) == 1:
                typ = typset.pop()
                if typ is not cls:
                    return typ(choras, keys)
            return super().__class_call__(choras, keys)

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

        @property
        def validate_contents(self, /):
            return _IncisionProtocol.CONTAINS(self.incision_manager)


    class Space(metaclass=_Sprite):

        chora: _Chora

        class __choret__(_Sampleable):

            @property
            def chora(self, /):
                return self.bound.chora

            def handle_tuple(self, incisor: tuple, /, *, caller):
                nspace = self.slyce_n(len(incisor))
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

            def slyce_n(self, incisor: int, /):
                return self.bound.SymForm(self.chora, incisor)

        def __incise_trivial__(self, /):
            if self.chora is self.SubmemberType:
                return self.MemberType
            return self


_ = Brace.register(tuple)


###############################################################################
###############################################################################
