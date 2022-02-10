###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionChain as _IncisionChain,
    Incisable as _Incisable,
    ChainIncisable as _ChainIncisable,
    )
from everest.utilities import pretty as _pretty, caching as _caching

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
  

    @classmethod
    def __class_init__(cls, /):
        with (Oid := cls.Oid).mutable:
            Oid.basememberspace = cls.__dict__.get('owner', _Fundament)
        super().__class_init__()
        cls._add_mroclass('Slyce')

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


    class Oid(metaclass=_Essence):


        SUBCLASSES = ('OpenForm', 'SymForm', 'AsymForm')

        @property
        def memberspace(self, /):
            return self.basememberspace

        def validate_contents(self, arg, /):
            try:
                it = iter(arg)
            except TypeError:
                return False
            return all(isinstance(subarg, self.memberspace) for subarg in it)

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


        class OpenForm(_Chora, metaclass=_Sprite):

            chora: _Chora = None

            @classmethod
            def __class_call__(cls, chora=None):
                if chora is None:
                    chora = cls.basememberspace
                elif not (
                        _IncisionProtocol.INCLUDES(cls.basememberspace)
                        (chora)
                        ):
                    raise TypeError(cls, chora)
                return super().__class_call__(chora)

            @property
            def memberspace(self, /):
                return self.chora

            @property
            def __incise_slyce__(self, /):
                return self._ptolemaic_class__

            class __choret__(_Sampleable):

                def handle_tuple(self, incisor: tuple, /, *, caller):
                    return _IncisionProtocol.INCISE(self.bound.SymForm(
                        self.bound.memberspace, (), len(incisor)
                        ))(incisor, caller=caller)

                def handle_dict(self, incisor: dict, /, *, caller):
                    return _IncisionProtocol.INCISE(self.bound.SymForm(
                        self.bound.memberspace, tuple(incisor)
                        ))(incisor, caller=caller)

                def handle_other(self, incisor: object, /, *, caller):
                    return _IncisionProtocol.INCISE(self.bound.memberspace)(
                        incisor, caller=caller
                        )

                def sample_slyce_chora(self, incisor: _Chora, /):
                    try:
                        bracetyp = _ArmatureProtocol.BRACE(incisor)
                    except AttributeError:
                        return self.bound.OpenForm(incisor)
                    else:
                        memberspace = self.bound.memberspace
                        if not (
                                _IncisionProtocol.INCLUDES(memberspace)
                                (bracetyp)
                                ):
                            raise TypeError(self.bound, type(incisor))
                        return bracetyp

                def slyce_n(self, incisor: Length, /):
                    return self.bound.SymForm(
                        self.bound.memberspace, (), incisor.n
                        )


        class SymForm(_Chora, metaclass=_Sprite):

            chora: _Chora
            labels: tuple = ()
            depth: int = None

            @classmethod
            def __class_call__(cls, chora, labels, depth=None, /):
                if not cls.basememberspace.__includes__(chora):
                    raise ValueError(chora)
                if depth is None:
                    depth = len(labels)
                typ = _ArmatureProtocol.BRACE(chora, cls.owner.owner).SymForm
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
                owner = cls.owner
                checker = _IncisionProtocol.INCLUDES(owner.owner)
                if not all(map(checker, choras)):
                    raise ValueError(choras)
                if len(typset := set(
                        _ArmatureProtocol.BRACE(chora, owner.owner).AsymForm
                        for chora in choras
                        )) == 1:
                    typ = typset.pop()
                    if typ is not cls:
                        return typ(choras, labels)
                return super().__class_call__(choras, labels)

            @property
            def depth(self, /):
                return len(self.choras)

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


        class Space(_ChainIncisable, metaclass=_Essence):

            @property
            @_caching.soft_cache()
            def __incision_manager__(self, /):
                return self.OpenForm(self.memberspace)


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


###############################################################################
###############################################################################
