###############################################################################
''''''
###############################################################################


import itertools as _itertools
import types as _types

from everest import incision as _incision
from everest.utilities import (
    pretty as _pretty,
    caching as _caching,
    FrozenNamespace as _FrozenNamespace,
    )

from everest.ptolemaic.compound import Compound as _Compound
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.atlantean import Binding as _Binding

from . import query as _query
from .chora import Chora as _Chora, ChainChora as _ChainChora
from . import choret as _choret
from .bythos import Bythos as _Bythos
from .algebraic import Algebraic as _Algebraic
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


def get_bracetyp_single(arg, default=None, /):
    try:
        return arg.__armature_brace__
    except (AttributeError, NotImplementedError) as exc:
        if default is None:
            raise exc
        return default


def get_bracetyp(ACls, arg: tuple, /):
    if len(typset := set(
            get_bracetyp_single(arg, ACls)
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
            return caller.__incise_slyce__(incisor)
        return caller.__incise_fail__(incisor)


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
        typ = get_bracetyp_single(arg, cls)
        if labels is None:
            return typ.Power(arg)
        labels = process_labels(labels)
        return typ.Symmetric(arg, labels)


    class Form(metaclass=_Essence):
        ...


    class Power(metaclass=_Compound):

        OVERCLASSES = ('Form',)

        content: object


    class Symmetric(metaclass=_Compound):

        OVERCLASSES = ('Form',)

        content: object
        labels: tuple

        def __init__(self, /):
            if isinstance(self.content, tuple):
                raise TypeError(self.content)
            super().__init__()


    class Asymmetric(metaclass=_Compound):

        OVERCLASSES = ('Form',)

        content: tuple
        labels: tuple


class Brace(BraceLike, _Algebraic, metaclass=_Bythos):


    MROCLASSES = ('Oid',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.Oid.register(cls)
        if (owner := cls.owner) is None:
            owner = PowerChora
        cls.__class_incision_manager__ = cls.Oid.Power(owner)


    class Form(_ChainChora):

        @property
        def __incision_manager__(self, /):
            return self.labels

        def __incise_slyce__(self, incisor, /):
            return self._ptolemaic_class__(self.content, incisor)

        def __len__(self, /):
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

        def __iter__(self, /):
            return _itertools.repeat(self.content, len(self))

        def __contains__(self, arg, /):
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
        def __contains__(self, /):
            return self.astuple().__contains__

        def __iter__(self, /):
            return iter(self.astuple())


    @_Algebraic.register
    class Oid(BraceLike, _Chora):


        class Form(_incision.Incisable, metaclass=_Essence):

            def __incise_retrieve__(self, incisor, /):
                return self._ptolemaic_class__.owner.owner(*incisor)

            @property
            def __armature_brace__(self, /):
                return self._ptolemaic_class__.owner.owner.__armature_truss__

            def __mod__(self, arg, /):
                return Brace.Oid(self, arg)

            def __rmod__(self, arg, /):
                return NotImplemented

            def __incise_trivial__(self, /):
                return self

            def __includes__(self, arg, /) -> bool:
                if isinstance(arg, _incision.Degenerate):
                    return arg.retrieve() in self
                owner = self._ptolemaic_class__.owner.owner
                if arg is owner:
                    return True
                return isinstance(arg, owner.Oid)

            def __contains__(self, arg, /):
                return isinstance(arg, self._ptolemaic_class__.owner.owner)


        class Power(_Chora):

            MROCLASSES = ('__incise__',)

            def _retrieve_repeatlike(self, incisor, /):
                raise NotImplementedError

            class __incise__(_choret.Basic):

                def handle_mapping(self,
                        incisor: _Binding, /, *, caller
                        ):
                    return (
                        self.boundowner(self.bound.content, tuple(incisor))
                        .__incise__(_query.Shallow(incisor), caller=caller)
                        )

                def handle_sequence(self,
                        incisor: tuple, /, *, caller
                        ):
                    return (
                        self.boundowner(
                            self.bound.content,
                            _get_intt_()[0:len(incisor)],
                            )
                        .__incise__(_query.Shallow(incisor), caller=caller)
                        )

                def handle_other(self, incisor: object, /, *, caller):
                    bound = self.bound
                    content = bound.content
                    caller = _incision.IncisionChain(
                        content,
                        _FrozenNamespace(
                            __incise_slyce__=bound._ptolemaic_class__,
                            __incise_retrieve__=bound._retrieve_repeatlike,
                            ),
                        caller,
                        )
                    return content.__incise__(incisor, caller=caller)

            def __contains__(self, arg, /):
                if not super().__contains__(arg):
                    return False
                return all(map(self.content.__contains__, arg))

            def __includes__(self, arg, /):
                if not super().__includes__(arg):
                    return False
                return self.content.__includes__(arg.content)

            def _repr_pretty_(self, p, cycle, root=None):
                if root is None:
                    root = self._ptolemaic_class__.__qualname__
                if cycle:
                    p.text(root + '{...}')
                    return
                with p.group(4, root + '(', ')'):
                    _pretty.pretty(self.content, p, cycle)


        class Symmetric(_Chora):

            MROCLASSES = ('__incise__',)

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
                return self.__incise__.active

            __incise__ = _choret.Multi

            def __contains__(self, arg, /):
                if not super().__contains__(arg):
                    return False
                return self.__incise__.__contains__(arg)

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


        class Asymmetric(_Chora, metaclass=_Compound):

            MROCLASSES = ('__incise__',)

            __incise__ = _choret.Multi

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
                return self.__incise__.active

            def __contains__(self, arg, /):
                if not super().__contains__(arg):
                    return False
                return self.__incise__.__contains__(arg)

            def __includes__(self, arg, /):
                if not super().__includes__(arg):
                    return False
                return self.__incise__.__includes__(arg)

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
