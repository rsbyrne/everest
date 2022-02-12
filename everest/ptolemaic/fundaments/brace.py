###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionChain as _IncisionChain,
    )
from everest.utilities import (
    pretty as _pretty,
    caching as _caching,
    )

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.armature import (
    ArmatureProtocol as _ArmatureProtocol,
    )
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Choric as _Choric,
    ChainChora as _ChainChora,
    Multi as _Multi,
    Sampleable as _Sampleable,
    )

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament


class Length(metaclass=_Sprite):

    n: int = 0


class Brace(_Fundament, _ChainChora, metaclass=_Sprite):


    content: tuple
    labels: tuple = ()

    _req_slots__ = ('ilabels',)


    @classmethod
    def __mroclass_init__(cls, /):
        super().__mroclass_init__()
        with (Oid := cls.Oid).mutable:
            Oid.basememberspace = cls.owner

    @classmethod
    def __class_init__(cls, /):
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

        basememberspace = _Fundament

        @property
        def memberspace(self, /):
            return self.basememberspace

        def __incise_retrieve__(self, incisor, /):
            return self._ptolemaic_class__.owner(
                incisor, getattr(self, 'labels', ())
                )


        class OpenForm(_Choric, metaclass=_Sprite):

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

            def _retrieve_repeatlike(self, incisor, /):
                raise NotImplementedError

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
                    caller = _IncisionChain(
                        caller,
                        __incise_slyce__=self.bound._ptolemaic_class__,
                        __incise_retrieve__=self.bound._retrieve_repeatlike,
                        )
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
                            raise ValueError(self.bound, type(incisor))
                        return bracetyp

            def __incise_contains__(self, arg, /):
                if not super().__incise_contains__(arg):
                    return False
                return all(
                    isinstance(sub, self.memberspace)
                    for sub in arg
                    )


        class SymForm(_Choric, metaclass=_Sprite):

            chora: _Chora
            labels: tuple = ()
            depth: int = None

            @classmethod
            def __class_call__(cls, chora, labels, depth=None, /):
                if not cls.basememberspace.__includes__(chora):
                    raise ValueError(cls, cls.basememberspace, chora)
                if depth is None:
                    depth = len(labels)
                typ = (
                    _ArmatureProtocol.BRACE(chora, cls.owner)
                    .Oid.SymForm
                    )
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

            def __incise_contains__(self, arg, /):
                if not super().__incise_contains__(arg):
                    return False
                return self.__incision_manager__.__incise_contains__(arg)


        class AsymForm(_Choric, metaclass=_Sprite):

            choras: tuple
            labels: tuple = ()

            @classmethod
            def __class_call__(cls, choras, labels=None):
                if labels is None:
                    if isinstance(choras, _collabc.Mapping):
                        choras, labels = tuple(choras.values()), tuple(choras)
                    else:
                        labels = ()
                checker = _IncisionProtocol.INCLUDES(cls.basememberspace)
                if not all(map(checker, choras)):
                    raise ValueError(cls.owner, cls.basememberspace, choras)
                if len(typset := set(
                        _ArmatureProtocol.BRACE(chora, cls.owner)
                        .Oid.AsymForm
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

            def __incise_contains__(self, arg, /):
                if not super().__incise_contains__(arg):
                    return False
                return self.__incision_manager__.__incise_contains__(arg)

            @property
            def depth(self, /):
                return len(self.choras)

            def keys(self, /):
                return self.labels

            def values(self, /):
                return self.choras

            def asdict(self, /):
                return dict(zip(self.keys(), self.values()))

            def _repr_pretty_(self, p, cycle, root=None):
                if root is None:
                    root = self.rootrepr
                if self.labels:
                    _pretty.pretty_kwargs(self.asdict(), p, cycle, root=root)
                else:
                    super()._repr_pretty_(p, cycle, root=root)


        class Space(metaclass=_Essence):

            @property
            @_caching.soft_cache()
            def __incision_manager__(self, /):
                return self.OpenForm(self.memberspace)


    class Slyce(_ChainChora, metaclass=_Sprite):

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
