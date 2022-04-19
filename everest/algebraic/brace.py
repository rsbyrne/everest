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
from .index import Index as _Index


def _get_intt_():
    global _Intt
    try:
        return _Intt
    except NameError:
        from .intt import Intt as _Intt
        return _Intt


def process_labels(arg, /):
    if arg is Ellipsis:
        return _get_intt_()[0:]
    if isinstance(arg, int):
        return _get_intt_()[0:arg]
    if isinstance(arg, tuple):
        return _Index(arg)
    return arg


def get_bracetyp(ACls, arg: tuple, /):
    if len(typset := set(
            _ArmatureProtocol.BRACE(arg, ACls)
            for subarg in arg
            )) == 1:
        return typset.pop()
    return ACls


class PowerChora(metaclass=_Bythos):

    @classmethod
    def __class_incise_slyce__(cls, incisor, /):
        return incisor

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        if isinstance(incisor, _Chora):
            return _IncisionProtocol.SLYCE(caller)(incisor)
        return IncisionProtocol.FAIL(caller)


class BraceLike(metaclass=_Essence):


    MROCLASSES = ('Form', 'Power', 'Symmetric', 'Asymmetric')

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.register(cls.Form)

    @classmethod
    def __class_call__(cls, arg, /, labels=None):
        if isinstance(arg, tuple):
            if labels is None:
                labels = len(arg)
            labels = process_labels(labels)
            return get_bracetyp(cls, arg).Asymmetric(arg, labels)
        typ = _ArmatureProtocol.BRACE(arg, cls)
        if labels is None:
            return typ.Power(arg)
        labels = process_labels(labels)
        return typ.Symmetric(arg, labels)


    class Form(metaclass=_Essence):
        ...


    class Power(metaclass=_Sprite):

        OVERCLASSES = ('Form',)

        content: object


    class Symmetric(metaclass=_Sprite):

        OVERCLASSES = ('Form',)

        content: object
        labels: tuple

        def __init__(self, /):
            if isinstance(self.content, tuple):
                raise TypeError(self.content)
            super().__init__()


    class Asymmetric(metaclass=_Sprite):

        OVERCLASSES = ('Form',)

        content: tuple
        labels: tuple


class Brace(BraceLike, _Fundament, metaclass=_Bythos):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        if (owner := cls.owner) is None:
            owner = PowerChora
        cls.__class_incision_manager__ = cls.Oid.Power(owner)


    class Form(_ChainChora):

        @property
        def __incision_manager__(self, /):
            return self.labels

        def __incise_slyce__(self, incisor, /):
            return self._ptolemaic_class__(self.content, incisor)

        def __incise_length__(self, /):
            return len(self.labels)

        @_caching.soft_cache()
        def asdict(self, /):
            return _types.MappingProxyType(dict(zip(
                self.labels, self.astuple()
                )))

        @property
        def shape(self, /):
            return (len(self.labels),)

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.__qualname__
            _pretty.pretty(self.asdict(), p, cycle, root=root)


    class Symmetric(metaclass=_Essence):

        def __incise_retrieve__(self, _=None, /):
            return self.content

        def __incise_iter__(self, /):
            return _itertools.repeat(self.content, len(self))

        def __incise_contains__(self, arg, /):
            return arg == self.content


    class Asymmetric(metaclass=_Essence):

        @property
        def __incise_retrieve__(self, /):
            return self.content.__getitem__

        @_caching.soft_cache()
        def astuple(self, /):
            labels = self.labels
            return tuple(map(
                self.content.__getitem__,
                map(labels.__getitem__, labels),
                ))

        @property
        def __incise_contains__(self, /):
            return self.astuple().__contains__

        def __incise_iter__(self, /):
            return iter(self.astuple())


    class Oid(BraceLike):


        class Form(_Incisable, metaclass=_Essence):

            def __incise_retrieve__(self, incisor, /):
                return self._ptolemaic_class__.owner.owner(*incisor)

            @property
            def __armature_brace__(self, /):
                return _ArmatureProtocol.TRUSS(
                    self._ptolemaic_class__.owner.owner
                    )

            def __mod__(self, arg, /):
                return Brace.Oid(self, arg)

            def __rmod__(self, arg, /):
                return NotImplemented


        class Power(_Choric):

            def _retrieve_repeatlike(self, incisor, /):
                raise NotImplementedError

            class __choret__(_Basic):

                def handle_mapping(self,
                        incisor: _Diict, /, *, caller
                        ):
                    return _IncisionProtocol.INCISE(self.boundowner(
                        self.bound.content,
                        tuple(incisor),
                        ))(_query.Shallow(incisor), caller=caller)

                def handle_sequence(self,
                        incisor: tuple, /, *, caller
                        ):
                    return _IncisionProtocol.INCISE(self.boundowner(
                        self.bound.content,
                        _get_intt_()[0:len(incisor)],
                        ))(_query.Shallow(incisor), caller=caller)

                def handle_other(self, incisor: object, /, *, caller):
                    bound = self.bound
                    content = bound.content
                    caller = _IncisionChain(
                        content,
                        _FrozenNamespace(
                            __incise_slyce__=bound._ptolemaic_class__,
                            __incise_retrieve__=bound._retrieve_repeatlike,
                            ),
                        caller,
                        )
                    return _IncisionProtocol.INCISE(content)(
                        incisor, caller=caller
                        )

            def __incise_contains__(self, arg, /):
                if not super().__incise_contains__(arg):
                    return False
                return all(
                    isinstance(sub, self.content)
                    for sub in arg
                    )

            def _repr_pretty_(self, p, cycle, root=None):
                if root is None:
                    root = self._ptolemaic_class__.__qualname__
                if cycle:
                    p.text(root + '{...}')
                    return
                with p.group(4, root + '(', ')'):
                    _pretty.pretty(self.content, p, cycle)


        class Symmetric(_Choric):

            @property
            def choras(self, /):
                return tuple(_itertools.repeat(self.content, self.depth))

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
                    _pretty.pretty(self.content, p, cycle)
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
                    self.content.__getitem__,
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


#         @classmethod
#         def symmetric(cls, arg, labels, /):
#             return (
#                 _ArmatureProtocol.BRACE(arg, cls.owner)
#                 .Symmetric(arg, labels)
#                 )

#         @classmethod
#         def asymmetric(cls, args, labels, /):
#             return (
#                 get_bracetyp(cls, args)
#                 .Asymmetric(args, labels)
#                 )


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