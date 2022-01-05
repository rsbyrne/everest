###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import inspect as _inspect
from collections import deque as _deque
import itertools as _itertools
import typing as _typing
import types as _types

from everest.utilities import (
    TypeMap as _TypeMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType, NotImplementedType,
    ObjectMask as _ObjectMask,
    )

from everest.ptolemaic.incision import *
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.eidos import Eidos as _Eidos


# def default_getmeth(obj, caller, incisor, /):
#     raise IncisorTypeException(incisor, obj, caller)


class CompositionHandler(IncisionHandler, metaclass=_Eidos):

    FIELDS = ('caller', 'fchora', 'gchora')

    @property
    def incise(self, /):
        return self.caller.incise

    @property
    def retrieve(self, /):
        return self.caller.retrieve

    @property
    def trivial(self, /):
        return self.caller.trivial

    @property
    def fail(self, /):
        return self.caller.fail


class SuperCompHandler(CompositionHandler):

    def incise(self, chora):
        return super().incise(chora.compose(self.gchora))

    def retrieve(self, index, /):
        return super().retrieve(index)


class SubCompHandler(CompositionHandler):

    FIELDS = ('submask',)

    def incise(self, chora):
        return super().incise(self.fchora.compose(chora))

    def retrieve(self, index, /):
        return self.fchora.__getitem__(index, caller=self.caller)

    def fail(self, chora, incisor, /):
        return (fchora := self.fchora)._ptolemaic_class__.__getitem__(
            self.submask,
            incisor,
            caller=SuperCompHandler(self.caller, fchora, self.gchora),
            )


class Composition(ChoraBase, metaclass=_Eidos):

    FIELDS = ('fchora', 'gchora')

    _req_slots__ = ('submask',)

    def __init__(self, /):
        gchora = self.gchora
        self.submask = _ObjectMask(
            self.fchora,
            __getitem__=gchora.__getitem__,
            )

    def __getitem__(self, incisor, /, *, caller=DefaultCaller):
        return (gchora := self.gchora).__getitem__(
            incisor,
            caller=SubCompHandler(caller, self.fchora, gchora, self.submask),
            )

def _wrap_process(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return meth(self, arg)(self, arg, caller=caller)
    return wrapper

def _wrap_getitem(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        incisor, protocol = meth(self, arg)
        return protocol(caller)(incisor)
    return wrapper

def _wrap_trivial(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return IncisionProtocol.TRIVIAL(caller)(self)
    return wrapper

def _wrap_incise(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return IncisionProtocol.INCISE(caller)(meth(self, arg))
    return wrapper

def _wrap_retrieve(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return IncisionProtocol.RETRIEVE(caller)(meth(self, arg))
    return wrapper

def _wrap_fail(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return IncisionProtocol.FAIL(caller)(self, arg)
    return wrapper

WRAPMETHS = dict(
    process=_wrap_process,
    getitem=_wrap_getitem,
    trivial=_wrap_trivial,
    incise=_wrap_incise,
    retrieve=_wrap_retrieve,
    fail=_wrap_fail,
    )


class Chora(ChoraBase, metaclass=_Essence):

    MERGETUPLES = ('PREFIXES',)
    PREFIXES = (
        'handle',
        *(meth.value for meth in IncisionProtocol),
        )

    def compose(self, other, /):
        return Composition(self, other)

    def handle_protocol(self, incisor: IncisionProtocol, /, *, caller):
        return incisor(caller)()

    def handle_none(self, incisor: NoneType, /, *, caller):
        '''Captures the special behaviour implied by `self[None]`.'''
        return IncisionProtocol.GENERIC(caller)()

    def trivial_notimplemented(self, incisor: NotImplementedType, /):
        '''Captures the special behaviour implied by `self[NotImplemented]`.'''
        pass

    def trivial_ellipsis(self, incisor: EllipsisType, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        pass

    def incise_chora(self, incisor: ChoraBase, /):
        '''Returns the composition of two choras, i.e. f(g(x)).'''
        return self.compose(incisor)

    def fail_ultimate(self, incisor: object, /):
        '''The ultimate fallback for unrecognised incision types.'''
        pass

    @classmethod
    def get_getmethnames(cls, /, preprefix=''):
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
        return methnames

    @classmethod
    def _yield_getmeths(cls, /,
            preprefix='', defaultwrap=(lambda x: x), hintprocess=(lambda x: x)
            ):
        methnames = cls.get_getmethnames(preprefix)
        seen = set()
        for prefix, deq in methnames.items():
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
        cls.getmeths = _TypeMap(cls._yield_getmeths())

    def __getitem__(self, arg, /, *, caller=DefaultCaller):
        return self.getmeths[type(arg)](self, arg, caller=caller)

#     @classmethod
#     def decorate(cls, other, /):

#         with other.mutable:

#             other.Chora = cls

#             exec('\n'.join((
#                 f"def __getitem__(self, arg, /):",
#                 f"    return self.chora.__getitem__(arg, caller=self)",
#                 )))
#             other.__getitem__ = eval('__getitem__')
#             if not hasattr(other, 'chora'):
#                 exec('\n'.join((
#                     f"@property",
#                     f"@_caching.soft_cache()",
#                     f"def chora(self, /):",
#                     f"    return self.Chora()",
#                     )))
#                 other.chora = eval('chora')

#             for methname in PROTOCOLMETHS:
#                 if not hasattr(other, methname):
#                     meth = getattr(Incisable, methname)
#                     setattr(other, methname, meth)

#         return other


class _GENERICCLASS_(Chora, metaclass=_Eidos):

    def compose(self, other, /):
        return other

    def retrieve_object(self, incisor: object, /):
        return incisor

    def __repr__(self, /):
        return 'GENERIC'


GENERIC = _GENERICCLASS_()


class Degenerator(IncisionHandler):

    __slots__ = ()

    def retrieve(self, index, /):
        return Degenerate(index)


DEGENERATOR = Degenerator()


class MultiChoraBase(ChoraBase):

    __slots__ = ()

    @property
    @_abc.abstractmethod
    def choras(self, /):
        raise NotImplementedError

    @property
    def depth(self, /):
        return len(self.choras)

    @property
    @_caching.soft_cache()
    def active(self, /):
        return tuple(not isinstance(cho, Degenerate) for cho in self.choras)

    @property
    @_caching.soft_cache()
    def activechoras(self, /):
        return tuple(_itertools.compress(self.choras, self.active))

    @property
    def activedepth(self, /):
        return len(self.activechoras)

    def yield_tuple_multiincise(self, /, *incisors):
        ninc, ncho = len(incisors), self.activedepth
        nell = incisors.count(...)
        if nell:
            ninc -= nell
            if ninc % nell:
                raise ValueError("Cannot resolve incision ellipses.")
            ellreps = (ncho - ninc) // nell
        chorait = iter(self.choras)
        try:
            for incisor in incisors:
                if incisor is ...:
                    count = 0
                    while count < ellreps:
                        chora = next(chorait)
                        if not isinstance(chora, Degenerate):
                            count += 1
                        yield chora
                    continue
                while True:
                    chora = next(chorait)
                    if isinstance(chora, Degenerate):
                        yield chora
                        continue
                    yield chora.__getitem__(incisor, caller=DEGENERATOR)
                    break
        except StopIteration:
#             raise ValueError("Too many incisors in tuple incision.")
            pass
        yield from chorait


class MultiBrace(Chora, MultiChoraBase, metaclass=_Eidos):

    FIELDS = (_inspect.Parameter('choraargs', 2),)

    @property
    def choras(self, /):
        return self.choraargs

    def handle_tuple(self, incisor: tuple, /, *, caller):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            incisor = tuple(cho.value for cho in choras)
            return caller.retrieve(self.retrieve_tuple(incisor))
        return caller.incise(self.incise_tuple(choras))

    def retrieve_tuple(self, incisor: tuple, /):
        return incisor

    def incise_tuple(self, incisor: tuple, /):
        return self._ptolemaic_class__(*incisor)


class MultiMapp(Chora, MultiChoraBase, metaclass=_Eidos):

    FIELDS = (_inspect.Parameter('chorakws', 4),)

    @property
    def choras(self, /):
        return tuple(self.chorakws.values())

    def handle_tuple(self, incisor: tuple, /, *, caller):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            incisor = dict(zip(
                self.chorakws,
                (cho.value for cho in choras),
                ))
            return caller.retrieve(self.retrieve_dict(incisor))
        incisor = dict(zip(self.chorakws, choras))
        return caller.incise(self.incise_dict(incisor))

    def yield_dict_multiincise(self, /, **incisors):
        chorakws = self.chorakws
        for name, incisor in incisors.items():
            chora = chorakws[name]
            yield name, chora.__getitem__(incisor, caller=Degenerator(chora))

    def handle_dict(self, incisor: dict, /, *, caller):
        choras = self.chorakws | dict(self.yield_dict_multiincise(**incisor))
        if all(isinstance(chora, Degenerate) for chora in choras.values()):
            incisor = {key: val.value for key, val in choras.items()}
            return caller.retrieve(self.retrieve_dict(incisor))
        return caller.incise(self.incise_dict(choras))

    def retrieve_dict(self, incisor: dict, /):
        return _types.MappingProxyType(incisor)

    def incise_dict(self, incisor: dict, /):
        return self._ptolemaic_class__(**incisor)


class Sliceable(Chora):

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
    def _yield_slcgetmeths(cls, /):
        return cls._yield_getmeths(
            'slice',
            hintprocess=_functools.partial(_typing.GenericAlias, slice),
            )

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.slcgetmeths = _TypeMap(cls._yield_slcgetmeths())



###############################################################################
###############################################################################


# class OrdChora(Chora):
#     '''Returns the `ord` of a character.'''

#     def retrieve_string(self, incisor: str, /) -> int:
#         return ord(incisor)


# class PowChora(Chora):

#     FIELDS = ('power',)

#     def retrieve_num(self, incisor: int) -> int:
#         return incisor**self.power


# class ChrChora(Chora):
#     '''Returns the `chr` of an integer.'''

#     def retrieve_int(self, incisor: int, /):
#         return chr(incisor)


# ChrChora()[PowChora(2)[OrdChora()]]['z']