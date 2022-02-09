###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    ChainIncisable as _ChainIncisable,
    )
from everest.utilities import pretty as _pretty

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.armature import (
    ArmatureProtocol as _ArmatureProtocol,
    )
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Multi as _Multi,
    Sampleable as _Sampleable,
    )

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament


class Length(metaclass=_Sprite):

    n: int = 0


class Brace(_Fundament, _ChainIncisable, metaclass=_Sprite):


    content: tuple
    labels: tuple = ()

    _req_slots__ = ('ilabels',)

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
        cls._add_mroclass('SymForm', (cls.Oid,))
        cls._add_mroclass('AsymForm', (cls.Oid,))
        with (Oid := cls.Oid).mutable:
            Oid.SubmemberType = cls.SubmemberType
        cls._add_mroclass('Slyce')

    @classmethod
    def make_class_incision_manager(cls, /):
        return cls.Space(cls.SubmemberType)

    def __init__(self, /):
        super().__init__()
        global Intt
        try:
            Intt = eval('Intt')
        except NameError:
            from everest.ptolemaic.fundaments.intt import Intt
        self.ilabels = Intt[0:len(self.content)]

    def asdict(self, /):
        return dict(zip(self.labels, self.content))

    def __getattr__(self, name, /):
        try:
            index = super().__getattr__('labels').index(name)
        except ValueError:
            return super().__getattr__(name)
        return super().__getattr__('content')[index]

    @property
    def __incision_manager__(self, /):
        return self.ilabels

    @property
    def __incise_retrieve__(self, /):
        return self.content.__getitem__

    def __incise_slyce__(self, incisor, /):
        return self.Slyce(self, incisor)

    @property
    def __incise_length__(self, /):
        return self.content.__len__

    @property
    def __incise_contains__(self, /):
        return self.content.__contains__

    @property
    def __incise_iter__(self, /):
        return self.content.__iter__

    @property
    def __incise_index__(self, /):
        return self.content.index

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        if self.labels:
            _pretty.pretty_kwargs(self.asdict(), p, cycle, root)
        else:
            _pretty.pretty_tuple(self.content, p, cycle, root)
          

    class Slyce(_ChainIncisable, metaclass=_Sprite):

        source: 'Brace'
        ilabels: _Chora

        @property
        def __incision_manager__(self, /):
            return self.ilabels

        @property
        def content(self, /):
            return tuple(map(self.source.content.__getitem__, self.ilabels))

        @property
        def __incise_retrieve__(self, /):
            return self.content.__getitem__

        def __incise_slyce__(self, incisor, /):
            return self._ptolemaic_class__(self.source, incisor)

        @property
        def __incise_length__(self, /):
            return self.content.__len__

        @property
        def __incise_contains__(self, /):
            return self.content.__contains__

        @property
        def __incise_iter__(self, /):
            return self.content.__iter__


    class Oid(metaclass=_Essence):

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

        def __incise_retrieve__(self, incisor, /):
            return self.owner(incisor, getattr(self, 'labels', ()))

        def __call__(self, arg, /):
            if not self.validate_contents(arg):
                raise ValueError(arg)
            return _IncisionProtocol.RETRIEVE(self)(arg)


    class SymForm(_Chora, metaclass=_Sprite):

        chora: _Chora
        labels: tuple = ()
        depth: int = None

        @classmethod
        def __class_call__(cls, chora, labels, depth=None, /):
            if not cls.SubmemberType.__includes__(chora):
                raise ValueError(chora)
            if depth is None:
                depth = len(labels)
            typ = _ArmatureProtocol.BRACE(chora, cls.MemberType).SymForm
            if typ is cls:
                return super().__class_call__(chora, labels, depth)
            return typ(chora, labels, depth)

        @property
        def choras(self, /):
            return tuple(_itertools.repeat(self.chora, self.depth))

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
        labels: tuple = ()

        @classmethod
        def __class_call__(cls, choras, labels=None):
            if labels is None:
                if isinstance(choras, _collabc.Mapping):
                    choras, labels = tuple(choras.values()), tuple(choras)
                else:
                    labels = ()
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
                symform = self.bound.SymForm(self.chora, (), len(incisor))
                return _IncisionProtocol.INCISE(symform)(
                    incisor, caller=caller
                    )

            def handle_dict(self, incisor: dict, /, *, caller):
                symform = self.bound.SymForm(self.chora, tuple(incisor))
                return _IncisionProtocol.INCISE(symform)(
                    incisor, caller=caller
                    )

            def sample_slyce_chora(self, incisor: _Chora, /):
                if not self.bound.SubmemberType.__includes__(incisor):
                    raise TypeError(self.bound, type(incisor))
                try:
                    return _ArmatureProtocol.BRACE(incisor)
                except AttributeError:
                    return self.bound._ptolemaic_class__(incisor)

            def slyce_n(self, incisor: Length, /):
                return self.bound.SymForm(self.chora, (), incisor.n)

        def __incise_trivial__(self, /):
            if self.chora is self.SubmemberType:
                return self.MemberType
            return self


_ = Brace.register(tuple)


###############################################################################
###############################################################################
