###############################################################################
''''''
###############################################################################


import itertools as _itertools
import types as _types

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionChain as _IncisionChain,
    Incisable as _Incisable,
    IncisionProtocolException as _IncisionProtocolException
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
from .bythos import Bythos as _Bythos
from .fundament import Fundament as _Fundament
from .allslyce import AllSlyce as _AllSlyce
from .index import Index as _Index


def _get_intt_():
    global _Intt
    try:
        return _Intt
    except NameError:
        from .intt import Intt as _Intt
        return _Intt


class BraceLike(metaclass=_Essence):


    MROCLASSES = ('Form',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Form = cls.Form
        for name in Form.SUBCLASSES:
            setattr(cls, name, getattr(Form, name))
        cls.register(Form)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.Form(*args, **kwargs)


    class Form(metaclass=_Essence):


        SUBCLASSES = ('Power', 'Symmetric', 'Asymmetric')

        @classmethod
        def process_labels(cls, arg, /):
            if arg is Ellipsis:
                return _get_intt_()[0:]
            if isinstance(arg, int):
                return _get_intt_()[0:arg]
            if isinstance(arg, tuple):
                return _Index(arg)
            return arg

        @classmethod
        def get_bracetyp(cls, arg: tuple, /):
            if len(typset := set(
                    _ArmatureProtocol.BRACE(arg, cls.owner)
                    for subarg in arg
                    )) == 1:
                return typset.pop()
            return cls

        @classmethod
        def __class_call__(cls, arg, /, labels=None):
            if isinstance(arg, tuple):
                if labels is None:
                    labels = len(arg)
                labels = cls.process_labels(labels)
                typ = cls.get_bracetyp(arg)
                return typ.Asymmetric(arg, labels)
            typ = _ArmatureProtocol.BRACE(arg, cls.owner)
            if labels is None:
                return typ.Power(arg)
            labels = cls.process_labels(labels)
            return typ.Symmetric(arg, labels)

        @classmethod
        def symmetric(cls, arg, labels, /):
            return (
                _ArmatureProtocol.BRACE(arg, cls.owner)
                .Symmetric(arg, labels)
                )

        @classmethod
        def asymmetric(cls, args, labels, /):
            return (
                cls.get_bracetyp(args)
                .Asymmetric(args, labels)
                )


        class Power(metaclass=_Sprite):

            arg: object


        class Symmetric(metaclass=_Sprite):

            arg: object
            labels: tuple

            def __init__(self, /):
                if isinstance(self.arg, tuple):
                    raise TypeError(self.arg)
                super().__init__()


        class Asymmetric(metaclass=_Sprite):

            args: tuple
            labels: tuple


class Brace(BraceLike, _Fundament, metaclass=_Bythos):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid


    class Form(_ChainChora):


        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.__qualname__
            _pretty.pretty(self.asdict(), p, cycle, root=root)


        class Asymmetric(metaclass=_Essence):

            @property
            def __incision_manager__(self, /):
                return self.labels

            @property
            def __incise_retrieve__(self, /):
                return self.args.__getitem__

            def __incise_slyce__(self, incisor, /):
                return self._ptolemaic_class__(self.args, incisor)

            @property
            @_caching.soft_cache()
            def content(self, /):
                labels = self.labels
                return tuple(map(
                    self.args.__getitem__,
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
                return len(self.labels)

            def __incise_iter__(self, /):
                return iter(self.content)

            @property
            def shape(self, /):
                return (len(self.labels),)


    class Oid(BraceLike, metaclass=_Bythos):


        @classmethod
        def __class_init__(cls, /):
            try:
                space = cls.owner.owner
            except AttributeError:
                space = None
            if space is None:
                space = _AllSlyce
            cls.basememberspace = space
            super().__class_init__()
            cls.__class_incision_manager__ = cls.Power(space)


        class Form(_Incisable, metaclass=_Essence):


            basememberspace = _AllSlyce

            @classmethod
            def __mroclass_init__(cls, /):
                cls.basememberspace = cls.owner.basememberspace
                super().__mroclass_init__()

            @property
            def memberspace(self, /):
                return self.basememberspace

            def __incise_retrieve__(self, incisor, /):
                return self._ptolemaic_class__.owner.owner(*incisor)

            @property
            def __armature_brace__(self, /):
                return _ArmatureProtocol.TRUSS(
                    self._ptolemaic_class__.owner.owner.owner
                    )

            def __mod__(self, arg, /):
                return Brace.Oid(self, arg)

            def __rmod__(self, arg, /):
                return NotImplemented

#             def __truediv__(self, arg, /):
#                 return Brace.Oid[(*self.choras, arg)]

#             def __rtruediv__(self, arg, /):
#                 return Brace.Oid[(arg, *self.choras)]


            class Power(_Choric):

                @property
                def memberspace(self, /):
                    return self.arg

                def _retrieve_repeatlike(self, incisor, /):
                    raise NotImplementedError

                class __choret__(_Basic):

                    def handle_mapping(self,
                            incisor: _Diict, /, *, caller
                            ):
                        return (
                            _IncisionProtocol.INCISE(
                                self._ptolemaic_class__.owner.owner(
                                    self.bound.memberspace,
                                    tuple(incisor),
                                    )
                                )
                            (_query.Shallow(incisor), caller=caller)
                            )

                    def handle_sequence(self,
                            incisor: tuple, /, *, caller
                            ):
                        symm = self.bound.symmetric(
                            self.bound.arg,
                            _get_intt_()[0:len(incisor)],
                            )
                        return _IncisionProtocol.INCISE(symm)(
                            _query.Shallow(incisor), caller=caller
                            )

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
                        _pretty.pretty(self.arg, p, cycle)


            class Symmetric(_Choric):

                @property
                def choras(self, /):
                    return tuple(_itertools.repeat(self.arg, self.depth))

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
                        _pretty.pretty(self.arg, p, cycle)
                        p.text(',')
                        p.breakable()
                        p.text('labels=')
                        _pretty.pretty(self.labels, p, cycle)
                        p.breakable()


            class Asymmetric(_Choric, metaclass=_Sprite):

                __choret__ = _Multi

                @property
                @_caching.soft_cache()
                def choras(self, /):
                    labels = self.labels
                    return tuple(map(
                        self.args.__getitem__,
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
                        root = self._ptolemaic_class__.__qualname__
                    _pretty.pretty(self.asdict(), p, cycle, root=root)


###############################################################################
###############################################################################


#                 def __truediv__(self, arg, /):
#                     return Brace[(*self.choras, arg)]

#                 def __rtruediv__(self, arg, /):
#                     return Brace[(arg, *self.choras)]

#                 def __sub__(self, arg, /):
#                     return Brace[self, arg]

#                 def __rsub__(self, arg, /):
#                     return Brace[arg, self]

# if isinstance(arg, int):
#     return Brace.Oid.SymForm(self.chora, self.depth * arg)

# if isinstance(arg, int):
#     return Brace[tuple(
#         _itertools.chain.from_iterable(
#             _itertools.repeat(self.choras, arg)
#             )
#         )]


                        # baseowner = self._ptolemaic_class__.owner.owner
                        # if tuple(map(incisor.__contains__, SPECIALMEMBERS)):
                        #     length = len(incisor)
                        #     if length == 2:
                        #         if incisor[0] is Ellipsis:
                        #             return baseowner.Symmetric(
                        #                 self.bound.arg,
                        #                 Intt[:0]
                        #                 )
                        #         if incisor[1] is Ellipsis
                        #     elif length == 3:
                        #         pass
                        #     raise ValueError(incisor)