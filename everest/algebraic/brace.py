###############################################################################
''''''
###############################################################################


import itertools as _itertools
import types as _types

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionChain as _IncisionChain,
    Incisable as _Incisable,
    )
from everest.utilities import (
    pretty as _pretty,
    caching as _caching,
    FrozenNamespace as _FrozenNamespace,
    )

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.bythos import Bythos as _Bythos
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


        SUBCLASSES = ('Open', 'Symmetric', 'Asymmetric')

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

        @classmethod
        def __class_call__(cls, arg, /, labels=None):
            if isinstance(arg, tuple):
                if labels is None:
                    labels = len(arg)
                labels = cls.process_labels(labels)
                if len(typset := set(
                        _ArmatureProtocol.BRACE(arg, cls.owner)
                        for subarg in arg
                        )) == 1:
                    typ = typset.pop()
                else:
                    typ = cls
                return typ.Asymmetric(arg, labels)
            typ = _ArmatureProtocol.BRACE(arg, cls.owner)
            if labels is None:
                return typ.Open(arg)
            labels = cls.process_labels(labels)
            return typ.Symmetric(arg, labels)


        class Open(metaclass=_Sprite):

            arg: object


        class Symmetric(metaclass=_Sprite):

            arg: object
            labels: tuple


        class Asymmetric(metaclass=_Sprite):

            args: tuple
            labels: tuple


class Brace(BraceLike, _Fundament, metaclass=_Bythos):


    basememberspace = _AllSlyce

    @classmethod
    def __mroclass_init__(cls, /):
        owner = cls.basememberspace = cls.owner
        super().__mroclass_init__()
        cls.__class_incision_manager__ = cls.Oid.Open(owner)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid.Open(_AllSlyce)


    class Form(_ChainChora):


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


        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.__qualname__
            _pretty.pretty(self.asdict(), p, cycle, root=root)


    class Oid(BraceLike):


        class Form(_Incisable, metaclass=_Essence):


            basememberspace = _AllSlyce

            @classmethod
            def __mroclass_init__(cls, /):
                if (outerowner := cls.owner.owner) is not None:
                    cls.basememberspace = outerowner.basememberspace
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


            class Open(_Choric):

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
                        return (
                            _IncisionProtocol.INCISE(
                                self._ptolemaic_class__.owner.owner(
                                    self.bound.memberspace,
                                    self.bound.process_labels(len(incisor)),
                                    )
                                )
                            (_query.Shallow(incisor), caller=caller)
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

                def __truediv__(self, arg, /):
                    return Brace[(*self.choras, arg)]

                def __rtruediv__(self, arg, /):
                    return Brace[(arg, *self.choras)]

                def __sub__(self, arg, /):
                    return Brace[self, arg]

                def __rsub__(self, arg, /):
                    return Brace[arg, self]

                def __mod__(self, arg, /):
                    return Brace.Oid(self, arg)

                def __rmod__(self, arg, /):
                    return NotImplemented


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

                def __truediv__(self, arg, /):
                    return Brace[(*self.choras, arg)]

                def __rtruediv__(self, arg, /):
                    return Brace[(arg, *self.choras)]

                def __sub__(self, arg, /):
                    return Brace[self, arg]

                def __rsub__(self, arg, /):
                    return Brace[arg, self]

                def __mod__(self, arg, /):
                    return Brace.Oid(self, arg)

                def __rmod__(self, arg, /):
                    return NotImplemented


###############################################################################
###############################################################################


# if isinstance(arg, int):
#     return Brace.Oid.SymForm(self.chora, self.depth * arg)

# if isinstance(arg, int):
#     return Brace[tuple(
#         _itertools.chain.from_iterable(
#             _itertools.repeat(self.choras, arg)
#             )
#         )]
