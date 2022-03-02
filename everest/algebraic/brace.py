###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc
import types as _types

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionChain as _IncisionChain,
    )
from everest.utilities import (
    pretty as _pretty,
    caching as _caching,
    FrozenNamespace as _FrozenNamespace,
    )

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.diict import Diict as _Diict

from .armature import (
    ArmatureProtocol as _ArmatureProtocol,
    )
from . import query as _query
from .chora import (
    Chora as _Chora,
    Choric as _Choric,
    ChainChora as _ChainChora,
    Basic as _Basic,
    Multi as _Multi,
    )
from .fundament import Fundament as _Fundament
from .allslyce import AllSlyce as _AllSlyce
from .index import Index as _Index


class Brace(_Fundament, _ChainChora, metaclass=_Sprite):


    basememberspace = _AllSlyce

    truecontent: tuple
    labels: tuple = None

    @classmethod
    def __mroclass_init__(cls, /):
        owner = cls.basememberspace = cls.owner
        super().__mroclass_init__()
        cls.__class_incision_manager__ = cls.Oid.OpenForm(owner)
        # owner.Brace = cls

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid.OpenForm(_AllSlyce)
        # cls._add_mroclass('Slyce')

    @classmethod
    def __class_call__(cls, truecontent, labels=None):
        if labels is None:
            labels = len(truecontent)
        labels = cls.Oid.process_labels(labels)
        return super().__class_call__(truecontent, labels)

    @property
    def __incision_manager__(self, /):
        return self.labels

    @property
    def __incise_retrieve__(self, /):
        return self.truecontent.__getitem__

    def __incise_slyce__(self, incisor, /):
        return self._ptolemaic_class__(self.truecontent, incisor)

    @property
    @_caching.soft_cache()
    def content(self, /):
        labels = self.labels
        return tuple(map(
            self.truecontent.__getitem__,
            map(labels.__getitem__, labels),
            ))

    @_caching.soft_cache()
    def asdict(self, /):
        return _types.MappingProxyType(dict(zip(
            self.labels, self.content
            )))

    @property
    def __incise_contains__(self, /):
        return self.content.__contains__

    def __incise_length__(self, /):
        return len(self.content)

    def __incise_iter__(self, /):
        return iter(self.content)

    @property
    def shape(self, /):
        return (len(self.labels),)

    # @property
    # def __incise_index__(self, /):
    #     return self.content.index

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty(self.asdict(), p, cycle, root=root)


    class Oid(metaclass=_Essence):


        SUBCLASSES = ('OpenForm', 'SymForm', 'AsymForm')

        basememberspace = _AllSlyce

        @classmethod
        def __mroclass_init__(cls, /):
            cls.basememberspace = cls.owner.basememberspace
            super().__mroclass_init__()

        @property
        def memberspace(self, /):
            return self.basememberspace

        def __incise_retrieve__(self, incisor, /):
            return self._ptolemaic_class__.owner(*incisor)

        @property
        def __armature_brace__(self, /):
            return _ArmatureProtocol.TRUSS(self._ptolemaic_class__.owner.owner)

        @classmethod
        def process_labels(cls, arg, /):
            if isinstance(arg, int):
                global Intt
                try:
                    Intt = eval('Intt')
                except NameError:
                    from .intt import Intt
                return Intt[0:arg]
            if isinstance(arg, tuple):
                return _Index(arg)
            return arg


        class OpenForm(_Choric, metaclass=_Sprite):

            chora: _Chora

            # @classmethod
            # def __class_call__(cls, chora):
            #     # elif not (
            #     #         _IncisionProtocol.INCLUDES(cls.basememberspace)
            #     #         (chora)
            #     #         ):
            #     #     raise TypeError(cls, cls.basememberspace, chora)
            #     print('-' * 3)
            #     print(repr(cls))
            #     print(repr(chora))
            #     try:
            #         print(repr(_ArmatureProtocol.BRACE(chora)))
            #     except Exception as exc:
            #         print(exc)
            #     print(repr(cls.owner))
            #     typ = (
            #         _ArmatureProtocol.BRACE(chora, cls.owner)
            #         .Oid.OpenForm
            #         )
            #     if typ is cls:
            #         return super().__class_call__(chora)
            #     return typ(chora)

            @property
            def memberspace(self, /):
                return self.chora

            def _retrieve_repeatlike(self, incisor, /):
                raise NotImplementedError

            class __choret__(_Basic):

                def handle_mapping(self,
                        incisor: _Diict, /, *, caller
                        ):
                    return _IncisionProtocol.INCISE(self.bound.SymForm(
                        self.bound.memberspace, tuple(incisor)
                        ))(_query.Shallow(incisor), caller=caller)

                def handle_sequence(self, incisor: tuple, /, *, caller):
                    return _IncisionProtocol.INCISE(self.bound.SymForm(
                        self.bound.memberspace, len(incisor)
                        ))(_query.Shallow(incisor), caller=caller)

                def handle_other(self, incisor: object, /, *, caller):
                    bound = self.bound
                    memberspace = bound.memberspace
                    caller = _IncisionChain(
                        memberspace,
                        _FrozenNamespace(
                            __incise_slyce__=bound._ptolemaic_class__,
                            __incise_retrieve__=bound._retrieve_repeatlike,
                            ),
                        caller,
                        )
                    return _IncisionProtocol.INCISE(memberspace)(
                        incisor, caller=caller
                        )

            def __incise_contains__(self, arg, /):
                if not super().__incise_contains__(arg):
                    return False
                return all(
                    isinstance(sub, self.memberspace)
                    for sub in arg
                    )

            def _repr_pretty_(self, p, cycle, root=None):
                if root is None:
                    root = self._ptolemaic_class__.__qualname__
                if cycle:
                    p.text(root + '{...}')
                    return
                with p.group(4, root + '(', ')'):
                    # p.breakable()
                    self.chora._repr_pretty_(p, cycle)
                    # p.breakable()


        class SymForm(_Choric, metaclass=_Sprite):

            chora: _Chora
            labels: tuple

            @classmethod
            def __class_call__(cls, chora, labels):
                # if not cls.basememberspace.__includes__(chora):
                #     raise ValueError(cls, cls.basememberspace, chora)
                labels = cls.process_labels(labels)
                typ = (
                    _ArmatureProtocol.BRACE(chora, cls.owner)
                    .Oid.SymForm
                    )
                if typ is cls:
                    return super().__class_call__(chora, labels)
                return typ(chora, labels)

            @property
            def choras(self, /):
                return tuple(_itertools.repeat(self.chora, self.depth))

            @property
            def depth(self, /):
                return len(self.labels)

            @property
            def shape(self, /):
                return (self.depth,)

            def keys(self, /):
                return self.labels

            def values(self, /):
                return self.choras

            @property
            def active(self, /):
                return self.__incision_manager__.active

            __choret__ = _Multi

            def __incise_contains__(self, arg, /):
                if not super().__incise_contains__(arg):
                    return False
                return self.__incision_manager__.__incise_contains__(arg)

            def _repr_pretty_(self, p, cycle, root=None):
                if root is None:
                    root = self._ptolemaic_class__.__qualname__
                if cycle:
                    p.text(root + '{...}')
                    return
                with p.group(4, root + '(', ')'):
                    p.breakable()
                    self.chora._repr_pretty_(p, cycle)
                    p.text(',')
                    p.breakable()
                    p.text('labels=')
                    self.labels._repr_pretty_(p, cycle)
                    p.breakable()


        class AsymForm(_Choric, metaclass=_Sprite):

            truechoras: tuple
            labels: tuple = None

            @classmethod
            def __class_call__(cls, truechoras, labels=None):
                # checker = _IncisionProtocol.INCLUDES(cls.basememberspace)
                # if not all(map(checker, choras)):
                #     raise ValueError(cls.owner, cls.basememberspace, choras)
                labels = cls.process_labels(
                    len(truechoras) if labels is None else labels
                    )
                if len(typset := set(
                        _ArmatureProtocol.BRACE(chora, cls.owner)
                        .Oid.AsymForm
                        for chora in truechoras
                        )) == 1:
                    typ = typset.pop()
                    if typ is not cls:
                        return typ(truechoras, labels)
                return super().__class_call__(truechoras, labels)
                                       
            __choret__ = _Multi

            @property
            @_caching.soft_cache()
            def choras(self, /):
                labels = self.labels
                return tuple(map(
                    self.truechoras.__getitem__,
                    map(labels.__getitem__, labels)
                    ))

            @property
            def active(self, /):
                return self.__incision_manager__.active

            def __incise_contains__(self, arg, /):
                if not super().__incise_contains__(arg):
                    return False
                return self.__incision_manager__.__incise_contains__(arg)

            @property
            def depth(self, /):
                return len(self.choras)

            @property
            def shape(self, /):
                return (self.depth,)

            @_caching.soft_cache()
            def asdict(self, /):
                return _types.MappingProxyType(dict(zip(
                    self.labels, self.choras
                    )))

            def _repr_pretty_(self, p, cycle, root=None):
                if root is None:
                    root = self._ptolemaic_class__.owner.__qualname__
                _pretty.pretty(self.asdict(), p, cycle, root=root)


###############################################################################
###############################################################################
