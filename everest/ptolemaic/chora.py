###############################################################################
''''''
###############################################################################


import functools as _functools
from collections import deque as _deque
import typing as _typing
import types as _types

from everest.utilities import (
    TypeMap as _TypeMap,
    NotNone, Null, NoneType, EllipsisType, NotImplementedType,
    )

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    )
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.eidos import Eidos as _Eidos


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


class Chora(_Incisable, metaclass=_Essence):

    MERGETUPLES = ('PREFIXES', 'REQMETHS')
    PREFIXES = (
        'handle',
        *(protocol.name.lower() for protocol in _IncisionProtocol),
        )

    def handle_none(self, incisor: type(None), /, *, caller):
        return _IncisionProtocol.DEFAULT(caller)()

    def handle_protocol(self, incisor: _IncisionProtocol, /, *, caller):
        return incisor(caller)()

    def trivial_ellipsis(self, incisor: EllipsisType, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        pass

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

    @property
    def retrievable(self, /):
        return bool(self.Chora.getmethnames['retrieve'])

    @property
    def slyceable(self, /):
        return bool(self.Chora.getmethnames['slyce'])

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.update_getmeth_names()
        cls.getmeths = _TypeMap(cls._yield_getmeths())
        assert all(hasattr(cls, meth) for meth in cls.REQMETHS)
        cls.Chora = cls

    def __incise__(self, incisor, /, *, caller):
        return self.Chora.getmeths[type(incisor)](self, incisor, caller=caller)

    @classmethod
    def compatible(cls, ACls, /):
        return isinstance(ACls, _Essence)

    @classmethod
    def decorate(cls, ACls: _Essence, /):
        if not cls.compatible(ACls):
            raise TypeError(
                f"Type {ACls} is incompatible for decoration with {cls}."
                )
        abstract = set()
        with ACls.mutable:
            ACls.Chora = cls
            for name in cls.REQMETHS:
                if not hasattr(ACls, name):
                    setattr(ACls, name, getattr(cls, name))
                    if name in ACls.__abstractmethods__:
                        abstract.add(name)
        if abstract:
            ACls.__abstractmethods__ = ACls.__abstractmethods__ | abstract
        assert issubclass(ACls, _Incisable)
        return ACls

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if hasattr(ACls, 'Chora'):
            return cls in ACls.Chora.__mro__
        return super().__subclasshook__(ACls)


class Sliceable(Chora):

    def handle_slice(self, incisor: slice, /, *, caller):
        return self.Chora.slcgetmeths[
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


@Chora.decorate
class Composition(_Incisable, metaclass=_Eidos):

    fobj: _Incisable
    gobj: _Incisable

    def __incise_trivial__(self, /):
        return self

    def __incise_slyce__(self, incisor, /):
        return Composition(self.fobj, self.gobj.__incise_slyce__(incisor))

    def __incise_retrieve__(self, incisor, /):
        return self.fobj[self.gobj.__incise_retrieve__(incisor)]

    @property
    def __incise__(self, /):
        return self.gobj.__incise__


class Composable(Chora):

    def slyce_compose(self, incisor: _Incisable, /):
        '''Returns the composition of two choras, i.e. f(g(x)).'''
        return Composition(self, incisor)


###############################################################################
###############################################################################


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