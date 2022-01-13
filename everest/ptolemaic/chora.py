###############################################################################
''''''
###############################################################################


import functools as _functools
from collections import deque as _deque
import typing as _typing
import types as _types
import itertools as _itertools
import abc as _abc
import weakref as _weakref

from everest.utilities import (
    TypeMap as _TypeMap, FrozenMap as _FrozenMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType, NotImplementedType,
    )

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    Composition as _Composition,
    )
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia


class Chora(metaclass=_Essence):

    MROCLASSES = ('Choret',)

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if cls is Chora:
            if not isinstance(ACls, _Essence):
                return False
            return getattr(ACls, '_ptolemaic_choret_decorated_', False)
        return NotImplemented

#     @classmethod
#     def __init_subclass__(cls, /, *_, **__):
#         raise TypeError("This class cannot be subclassed.")


class Choret(_Sprite):

    def __set_name__(cls, owner, name, /):
        if isinstance(owner, _Essence):
            if name == 'Choret':
                cls.decorate(owner)


class ChoretBase(metaclass=Choret):

    BOUNDREQS = ()

    bound: object

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        @property
#         @_caching.soft_cache()
        def __defer_incise__(self, /):
            return self.Choret(self)
        cls.decoratemeths = dict(
            __defer_incise__=__defer_incise__,
            __getitem__=_Incisable.__getitem__,
            )

    @classmethod
    def compatible(cls, ACls, /):
        if not isinstance(ACls, _Essence):
            return False
        direc = dir(ACls)
        slots = getattr(ACls, '_req_slots__', ())
        fields = getattr(ACls, 'fields', ())
        for name in cls.BOUNDREQS:
            if name not in direc:
                if name not in slots:
                    if name not in fields:
                        return False
        return True

    @classmethod
    def decorate(cls, ACls, /):
        if not cls.compatible(ACls):
            raise TypeError(f"Type {ACls} incompatible with chora {cls}.")
        abstract = set()
        if hasattr(ACls, '__choret_decorate__'):
            ACls.__choret_decorate__(cls)
            return ACls
        with ACls.mutable:
            ACls.Choret = cls
            for name, obj in cls.decoratemeths.items():
                setattr(ACls, name, obj)
            ACls._ptolemaic_choret_decorated_ = True
        return ACls

    @_abc.abstractmethod
    def __incise__(self, *_, **__):
        raise NotImplementedError

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if isinstance(cls, Choret):
            if not isinstance(ACls, Chora):
                return False
            return issubclass(ACls.Choret, cls)
        return super().__subclasshook(ACls)


def _wrap_trivial(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, _, /, *, caller):
        return _IncisionProtocol.TRIVIAL(caller)()
    return wrapper

def _wrap_slyce(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return _IncisionProtocol.SLYCE(caller)(meth(self, arg))
    return wrapper

def _wrap_retrieve(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return _IncisionProtocol.RETRIEVE(caller)(meth(self, arg))
    return wrapper

def _wrap_fail(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return _IncisionProtocol.FAIL(caller)(arg, meth(self, arg))
    return wrapper

WRAPMETHS = dict(
    trivial=_wrap_trivial,
    slyce=_wrap_slyce,
    retrieve=_wrap_retrieve,
    fail=_wrap_fail,
    )


class Basic(metaclass=Choret):

    MERGETUPLES = ('PREFIXES', 'BOUNDREQS')
    PREFIXES = ('handle', *WRAPMETHS)

    @property
    def __getitem__(self, /):
        raise NotImplementedError

    def handle_none(self, incisor: type(None), /, *, caller):
        return _IncisionProtocol.GENERIC(caller)()

    def handle_protocol(self, incisor: _IncisionProtocol, /, *, caller):
        return incisor(caller)()

    def trivial_ellipsis(self, incisor: EllipsisType, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        pass

    def slyce_compose(self, incisor: _Incisable, /):
        '''Returns the composition of two choras, i.e. f(g(x)).'''
        return _Composition(self.bound, incisor)

    def fail_ultimate(self, incisor: object, /):
        '''The ultimate fallback for unrecognised incision types.'''
        return None

    @classmethod
    def update_getmeth_names(cls, /, preprefix=''):
        prefixes = cls.PREFIXES
        methnames = {prefix: _deque() for prefix in prefixes}
        adjprefixes = tuple(
            preprefix + ('_' if preprefix else '') + prefix + '_'
            for prefix in prefixes
            )
        for name in cls.attributes:
            for prefix, deq in zip(adjprefixes, methnames.values()):
                if name.startswith(prefix):
                    deq.append(name)
        setattr(cls,
            preprefix + 'getmethnames',
            _types.MappingProxyType({
                name: tuple(deq) for name, deq in methnames.items()
                })
           )

    @classmethod
    def _yield_getmeths(cls, /,
            preprefix='', defaultwrap=(lambda x: x),
            hintprocess=(lambda x: x), 
            ):
        methnames = getattr(cls, preprefix + 'getmethnames')
        seen = set()
        for prefix, deq in methnames.items():
            if not deq:
                continue
            wrap = WRAPMETHS.get(prefix, defaultwrap)
            for name in deq:
                meth = getattr(cls, name)
                hint = hintprocess(meth.__annotations__.get('incisor', cls))
                if hint not in seen:
                    yield hint, wrap(meth)
                    seen.add(hint)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.update_getmeth_names()
        cls.getmeths = _TypeMap(cls._yield_getmeths())

    @property
    def retrievable(self, /):
        return bool(self.getmethnames['retrieve'])

    @property
    def slyceable(self, /):
        return bool(self.getmethnames['slyce'])

    def __incise__(self, incisor, /, *, caller):
        return self.getmeths[type(incisor)](
            self, incisor, caller=caller
            )


# class Composition(_Incisable, metaclass=_Sprite):

#     fobj: _Incisable
#     gobj: _Incisable

#     @property
#     def __incise__(self, /):
#         return self.gobj

#     def __incise_trivial__(self, /):
#         return self

#     def __incise_slyce__(self, incisor, /):
#         return self._ptolemaic_class__(
#             self.fobj,
#             _IncisionProtocol.SLYCE(self.gobj)(incisor),
#             )

#     def __incise_retrieve__(self, incisor, /):
#         return self.fobj[
#             _IncisionProtocol.RETRIEVE(self.gobj)(incisor)
#             ]


class Sliceable(Basic):

    def handle_slice(self, incisor: slice, /, *, caller):
        return self.slcgetmeths[
            tuple(map(type, (incisor.start, incisor.stop, incisor.step)))
            ](self, incisor, caller=caller)

    def slice_trivial_none(self, incisor: (NoneType, NoneType, NoneType)):
        '''Captures the special behaviour implied by `self[:]`.'''
        pass

    def slice_fail_ultimate(self, incisor: (object, object, object)):
        '''The ultimate fallback for unrecognised slice types.'''
        pass

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.update_getmeth_names('slice')
        cls.slcgetmeths = _TypeMap(cls._yield_getmeths(
            'slice',
            hintprocess=_functools.partial(_typing.GenericAlias, slice),
            ))


###############################################################################
###############################################################################


#     @classmethod
#     def _yield_choricmeths(cls, /):
#         for name in cls.attributes:
#             if name.startswith('choric_'):
#                 yield 'choric_'.removeprefix(pref), getattr(cls, name)

#         cls.choricmeths = _FrozenMap(cls._yield_choricmeths())

#     @classmethod
#     def compatible(cls, ACls, /):
#         if not isinstance(ACls, _Ousia):
#             raise TypeError(
#                 f"Only instances of `Ousia` are compatible with {cls}."
#                 )
#         if not all(slot in ACls._req_slots__ for slot in cls.CHORICSLOTS):
#             raise TypeError(
#                 f"The Chora class {cls} expects the following _req_slots__: "
#                 f"cls.CHORICSLOTS"
#                 )
#         return True

#     def __new__(cls, arg, /):
#         if isinstance(arg, _Essence):
#             return cls.decorate(arg)
#         return super().__new__(cls, arg)

#     @classmethod
#     def decorate(cls, ACls: _Essence):
#         if not cls.compatible(ACls):
#             raise TypeError(
#                 f"Type {ACls} is incompatible for decoration with {cls}."
#                 )
#         abstract = set()
#         attributes = ACls.attributes
#         with ACls.mutable:
#             for name in _Incisable.REQMETHS:
#                 if name not in attributes:
#                     meth = getattr(_Incisable, name)
#                     if name in _Incisable.__abstractmethods__:
#                         abstract.add(name)
#                     setattr(ACls, name, meth)
#                     if name in ACls.__abstractmethods__:
#                         abstract.add(name)
#             for name, meth in cls.choricmeths.items():
#                 if name not in attributes:
#                     if name in cls.__abstractmethods__:
#                         abstract.add(name)
#                     setattr(ACls, name, meth)
#             if abstract:
#                 ACls.__abstractmethods__ = ACls.__abstractmethods__ | abstract
#         assert issubclass(ACls, _Incisable)
#         return ACls


# class CompositionHandler(IncisionHandler, metaclass=_Eidos):

#     FIELDS = ('caller', 'fchora', 'gchora')

#     @property
#     def incise(self, /):
#         return self.caller.incise

#     @property
#     def retrieve(self, /):
#         return self.caller.retrieve

#     @property
#     def trivial(self, /):
#         return self.caller.trivial

#     @property
#     def fail(self, /):
#         return self.caller.fail


# class SuperCompHandler(CompositionHandler):

#     def incise(self, chora):
#         return super().incise(chora.compose(self.gchora))

#     def retrieve(self, index, /):
#         return super().retrieve(index)


# class SubCompHandler(CompositionHandler):

#     FIELDS = ('submask',)

#     def incise(self, chora):
#         return super().incise(self.fchora.compose(chora))

#     def retrieve(self, index, /):
#         return self.fchora.__getitem__(index, caller=self.caller)

#     def fail(self, chora, incisor, /):
#         return (fchora := self.fchora)._ptolemaic_class__.__getitem__(
#             self.submask,
#             incisor,
#             caller=SuperCompHandler(self.caller, fchora, self.gchora),
#             )


# class Composition(ChoraBase, metaclass=_Eidos):

#     FIELDS = ('fchora', 'gchora')

#     _req_slots__ = ('submask',)

#     def __init__(self, /):
#         gchora = self.gchora
#         self.submask = _ObjectMask(
#             self.fchora,
#             __getitem__=gchora.__getitem__,
#             )

#     def __getitem__(self, incisor, /, *, caller=DefaultCaller):
#         return (gchora := self.gchora).__getitem__(
#             incisor,
#             caller=SubCompHandler(caller, self.fchora, gchora, self.submask),
#             )