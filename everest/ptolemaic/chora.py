###############################################################################
''''''
###############################################################################


import abc as _abc
from enum import Enum as _Enum
import functools as _functools
import inspect as _inspect
import collections as _collections
import itertools as _itertools
import typing as _typing
import types as _types
from collections import deque as _deque
from collections import abc as _collabc

from everest.utilities import (
    TypeMap as _TypeMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType, NotImplementedType,
    ObjectMask as _ObjectMask
    )
from everest import epitaph as _epitaph

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.armature import Armature as _Armature

from everest import exceptions as _exceptions


class IncisionProtocol(_Enum):

    TRIVIAL = 'trivial'
    INCISE = 'incise'
    RETRIEVE = 'retrieve'
    FAIL = 'fail'

    @classmethod
    def complies(cls, ACls, /):
        for meth in cls:
            for Base in ACls.__mro__:
                if meth.value in Base.__dict__:
                    continue
            return NotImplemented
        return True

#     def __init__(self, value, /):
#         self.lower = self.name.lower()
#         super().__init__(value)

    def __call__(self, on: _collabc.Callable, /):
        return getattr(on, self.value)


class IncisionException(_exceptions.ExceptionRaisedby):

    __slots__ = ('chora',)

    def __init__(self, chora=None, /, *args):
        self.chora = chora
        super().__init__(*args)

    def message(self, /):
        yield from super().message()
        yield 'during incision'
        chora = self.chora
        if chora is None:
            pass
        elif chora is not self.raisedby:
            yield ' '.join((
                f'via the hosted incisable `{repr(chora)}`',
                f'of type `{repr(type(chora))}`,',
                ))


class IncisorTypeException(IncisionException, TypeError):

    __slots__ = ('incisor',)

    def __init__(self, incisor, /, *args):
        self.incisor = incisor
        super().__init__(*args)
    
    def message(self, /):
        incisor = self.incisor
        yield from super().message()
        yield ' '.join((
            f'when object `{repr(incisor)}`',
            f'of type `{repr(type(incisor))}`',
            f'was passed as an incisor',
            ))


class IncisionHandler(_abc.ABC):

    def incise(self, chora, /):
        return chora

    def retrieve(self, index, /):
        return index

    def trivial(self, chora, /):
        return self

    def fail(self, chora, incisor, /):
        raise IncisorTypeException(incisor, chora, self)

    @classmethod
    def __subclasshook__(cls, ACls):
        if cls is not IncisionHandler:
            return NotImplemented
        return IncisionProtocol.complies(ACls)


class ChoraBase(_abc.ABC):

    @_abc.abstractmethod
    def __getitem__(self, arg, /, *, caller=None):
        raise NotImplementedError


class ChainIncisionHandler(IncisionHandler, _deque):

    def incise(self, chora, /):
        for obj in reversed(self):
            chora = obj.incise(chora)
        return chora

    def retrieve(self, index, /):
        for obj in reversed(self):
            index = obj.retrieve(index)
        return index

    def trivial(self, chora, /):
        return self[0]


class DefaultCaller:

    @classmethod
    def incise(cls, chora, /):
        return chora

    @classmethod
    def retrieve(cls, index, /):
        return index

    @classmethod
    def trivial(cls, chora, /):
        return chora

    @classmethod
    def fail(cls, chora, incisor, /):
        raise IncisorTypeException(incisor, chora, cls)


class Incisable(ChoraBase, IncisionHandler):

    def retrieve(self, index, /):
        raise Element(self, index)

    def incise(self, chora, /):
        return Incision(self, chora)

    @property
    @_abc.abstractmethod
    def chora(self, /) -> 'Incisable':
        raise NotImplementedError

    def __getitem__(self, arg, /, *, caller: IncisionHandler = None):
#         assert hasattr(arg, 'chora')
        if caller is None:
            caller = self
        elif isinstance(caller, ChainIncisionHandler):
            caller.append(self)
        else:
            caller = ChainIncisionHandler((caller, self))
        return self.chora.__getitem__(arg, caller=caller)

    @classmethod
    def __subclasshook__(cls, ACls):
        if cls is not Incisable:
            return NotImplemented
        if not IncisionHandler.__subclasshook__(ACls):
            return NotImplemented
        if all(
                any(meth in Base.__dict__ for Base in ACls.__mro__)
                for meth in ('__getitem__', 'chora')
                ):
            return True
        return NotImplemented

    def __contains__(self, arg: _collabc.Hashable, /):
        if isinstance(arg, Element):
            return arg.incised is self
        return NotImplemented


class Degenerate(ChoraBase):

    __slots__ = ('value', '_epitaph')

    def __init__(self, value, /):
        self.value = value

    def __getitem__(self, arg=None, /, *, caller=DefaultCaller):
        if arg is None:
            return caller.retrieve(self.value)
        return caller.fail(self, arg)

    def get_epitaph(self, /):
        return _epitaph.TAPHONOMY.callsig_epitaph(type(self), self.value)

    @property
    def epitaph(self, /):
        try:
            return self._epitaph
        except AttributeError:
            out = self._epitaph = self.get_epitaph()
            return out

    def __repr__(self, /):
        return f"{type(self).__name__}({repr(self.value)})"


class Element(metaclass=_Armature):

    incised: Incisable
    index: _collabc.Hashable


class Incision(Incisable, metaclass=_Armature):

    incised: Incisable
    chora: Incisable

    @property
    def retrieve(self, /):
        return self.incised.retrieve

    @property
    def incise(self, /):
        return self.incised.incise

    @property
    def __getitem__(self, /):
        return _functools.partial(self.chora.__getitem__, caller=self.incised)


def default_getmeth(obj, caller, incisor, /):
    raise IncisorTypeException(incisor, obj, caller)


class CompositionHandler(IncisionHandler, metaclass=_Armature):

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


class Composition(ChoraBase, metaclass=_Armature):

    FIELDS = ('fchora', 'gchora')

    __slots__ = ('submask',)

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


class Chora(ChoraBase, metaclass=_Armature):

    MERGETUPLES = ('PREFIXES',)
    PREFIXES = ('process', 'getitem', *(meth.value for meth in IncisionProtocol))

    def compose(self, other, /):
        return Composition(self, other)

    def trivial_notimplemented(self, incisor: NotImplementedType, /):
        '''Captures the special behaviour implied by `self[NotImplemented]`.'''
        pass

    def trivial_none(self, incisor: NoneType, /):
        '''Captures the special behaviour implied by `self[None]`.'''
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
        methnames = {prefix: _collections.deque() for prefix in prefixes}
        adjprefixes = tuple(map(preprefix.__add__, prefixes))
        for name in cls.attributes:
            for prefix, deq in zip(adjprefixes, methnames.values()):
                if name.startswith(prefix):
                    if name is prefix:
                        continue
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
                hint = hintprocess(meth.__annotations__['incisor'])
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


class Degenerator(IncisionHandler):

    def retrieve(self, index, /):
        return Degenerate(index)


DEGENERATOR = Degenerator()


class MultiChoraBase(ChoraBase):

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


class MultiBrace(Chora, MultiChoraBase):

    FIELDS = (_inspect.Parameter('choraargs', 2),)

    @property
    def choras(self, /):
        return self.choraargs

    def getitem_tuple(self, incisor: tuple, /) -> tuple[object, IncisionProtocol]:
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            return tuple(cho.value for cho in choras), IncisionProtocol.RETRIEVE
        return self._ptolemaic_class__(*choras), IncisionProtocol.INCISE


class MultiMapp(Chora, MultiChoraBase):

    FIELDS = (_inspect.Parameter('chorakws', 4),)

    @property
    def choras(self, /):
        return tuple(self.chorakws.values())

    def getitem_tuple(self, incisor: tuple, /) -> tuple[object, IncisionProtocol]:
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            out = _types.MappingProxyType(dict(zip(
                self.chorakws,
                (cho.value for cho in choras),
                )))
            return out, IncisionProtocol.RETRIEVE
        out = self._ptolemaic_class__(**dict(
            zip(self.chorakws, choras)
            ))
        return out, IncisionProtocol.INCISE

    def yield_dict_multiincise(self, /, **incisors):
        chorakws = self.chorakws
        for name, incisor in incisors.items():
            chora = chorakws[name]
            yield name, chora.__getitem__(incisor, caller=Degenerator(chora))

    def getitem_dict(self, incisor: dict, /):
        choras = self.chorakws | dict(self.yield_dict_multiincise(**incisor))
        if all(isinstance(chora, Degenerate) for chora in choras.values()):
            out = caller.retrieve(
                {key: val.value for key, val in choras.items()}
                )
            return out, IncisionProtocol.RETRIEVE
        out = self._ptolemaic_class__(**choras)
        return out, IncisionProtocol.INCISE


class Sliceable(Chora):

    def process_slice(self, incisor: slice, /):
        return self.slcgetmeths[
            tuple(map(type, (incisor.start, incisor.stop, incisor.step)))
            ]

    def slice_trivial_none(self, incisor: (NoneType, NoneType, NoneType)):
        '''Captures the special behaviour implied by `self[:]`.'''
        pass

    def slice_fail_ultimate(self, incisor: (object, object, object)):
        '''The ultimate fallback for unrecognised slice types.'''
        pass

    @classmethod
    def _yield_slcgetmeths(cls, /):
        return cls._yield_getmeths(
            'slice_',
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