###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import inspect as _inspect
import collections as _collections
import itertools as _itertools
import typing as _typing
import types as _types
from collections import deque as _deque

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


PROTOCOLMETHS = ('trivial', 'incise', 'retrieve', 'fail')


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

    def trivial(self, /):
        return self

    def fail(self, chora, incisor, /):
        raise IncisorTypeException(incisor, chora, self)

    @classmethod
    def __subclasshook__(cls, C):
        if cls is not IncisionHandler:
            return NotImplemented
        if all(
                any(meth in B.__dict__ for B in C.__mro__)
                for meth in PROTOCOLMETHS
                ):
            return True
        else:
            return NotImplemented


class ChainIncisionHandler(IncisionHandler, _deque):

    def incise(self, chora, /):
        for obj in reversed(self):
            chora = obj.incise(chora)
        return chora

    def retrieve(self, index, /):
        for obj in reversed(self):
            index = obj.retrieve(index)
        return index

    def trivial(self, /):
        return self[0]


DEFAULTCALLER = IncisionHandler()


class ChoraBase:
    ...
#     @_abc.abstractmethod
#     def __getitem__(self, arg, caller: IncisionHandler = DEFAULTCALLER):
#         raise NotImplementedError


class Degenerate(ChoraBase):

    __slots__ = ('value', '_epitaph')

    def __init__(self, value, /):
        self.value = value

    def __getitem__(self, arg=None, /, *, caller=DEFAULTCALLER):
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


class Incision(_ObjectMask, ChoraBase):

    def __init__(self, obj, chora, /):
        epitaph = _epitaph.TAPHONOMY.callsig_epitaph(type(self), obj, chora)
        super().__init__(
            obj, epitaph=epitaph,
            chora=chora, __getitem__=chora.__getitem__,
            )


class Incisable(IncisionHandler, ChoraBase):

    @_abc.abstractmethod
    def retrieve(self, index, /):
        raise NotImplementedError

    def incise(self, chora, /):
        return Incision(self, chora)

    @property
    @_abc.abstractmethod
    def chora(self, /) -> ChoraBase:
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

    def __getitem__(self, incisor, /, *, caller=DEFAULTCALLER):
        return (gchora := self.gchora).__getitem__(
            incisor,
            caller=SubCompHandler(caller, self.fchora, gchora, self.submask),
            )


def _wrap_trivial(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, caller, /, *_):
        return caller.trivial()
    return wrapper

def _wrap_incise(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, caller, arg, /):
        return caller.incise(meth(self, arg))
    return wrapper

def _wrap_retrieve(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, caller, arg, /):
        return caller.retrieve(meth(self, arg))
    return wrapper

def _wrap_fail(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, caller, arg, /):
        return caller.fail(self, arg)
    return wrapper

WRAPMETHS = dict(
    trivial=_wrap_trivial,
    incise=_wrap_incise,
    retrieve=_wrap_retrieve,
    fail=_wrap_fail,
    )


class Chora(ChoraBase, metaclass=_Armature):

    MERGETUPLES = ('PREFIXES',)
    PREFIXES = ('handle', 'trivial', 'incise', 'retrieve', 'fallback', 'fail')

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
    def _yield_getmeths(cls, /, preprefix='', defaultwrap=(lambda x: x)):
        methnames = cls.get_getmethnames(preprefix)
        seen = set()
        for prefix, deq in methnames.items():
            wrap = WRAPMETHS.get(prefix, defaultwrap)
            for name in deq:
                meth = getattr(cls, name)
                hint = meth.__annotations__['incisor']
                if hint not in seen:
                    yield hint, wrap(meth)
                    seen.add(hint)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.getmeths = _TypeMap(cls._yield_getmeths())

    def __getitem__(self, arg, /, *, caller=DEFAULTCALLER):
        return self.getmeths[type(arg)](self, caller, arg)

    @classmethod
    def decorate(cls, other, /):

        with other.mutable:

            other.Chora = cls

            exec('\n'.join((
                f"def __getitem__(self, arg, /):",
                f"    return self.chora.__getitem__(arg, caller=self)",
                )))
            other.__getitem__ = eval('__getitem__')
            if not hasattr(other, 'chora'):
                exec('\n'.join((
                    f"@property",
                    f"@_caching.soft_cache()",
                    f"def chora(self, /):",
                    f"    return self.Chora()",
                    )))
                other.chora = eval('chora')

            for methname in PROTOCOLMETHS:
                if not hasattr(other, methname):
                    meth = getattr(Incisable, methname)
                    setattr(other, methname, meth)

        return other


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

    def handle_tuple(self, caller, incisor: tuple, /):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            return caller.retrieve(tuple(cho.value for cho in choras))
        return caller.incise(self.__class_call__(*choras))


class MultiMapp(Chora, MultiChoraBase):

    FIELDS = (_inspect.Parameter('chorakws', 4),)

    @property
    def choras(self, /):
        return tuple(self.chorakws.values())

    def handle_tuple(self, caller, incisor: tuple, /):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            return caller.retrieve(_types.MappingProxyType(dict(zip(
                self.chorakws,
                (cho.value for cho in choras),
                ))))
        return caller.incise(self.__class_call__(**dict(
            zip(self.chorakws, choras)
            )))

    def yield_dict_multiincise(self, /, **incisors):
        chorakws = self.chorakws
        for name, incisor in incisors.items():
            chora = chorakws[name]
            yield name, chora.__getitem__(incisor, caller=Degenerator(chora))

    def handle_dict(self, caller, incisor: dict, /):
        choras = self.chorakws | dict(self.yield_dict_multiincise(**incisor))
        if all(isinstance(chora, Degenerate) for chora in choras.values()):
            return caller.retrieve(
                {key: val.value for key, val in choras.items()}
                )
        return caller.incise(self.__class_call__(**choras))


slcgen = _functools.partial(_typing.GenericAlias, slice)


class Sliceable(Chora):

    def handle_slice(self, caller, incisor: slice, /):
        typs = tuple(map(type, (incisor.start, incisor.stop, incisor.step)))
        return self.slcgetmeths[typs](self, caller, incisor)

    def slice_trivial_none(self,
            incisor: slcgen((NoneType, NoneType, NoneType)),
            ):
        '''Captures the special behaviour implied by `self[:]`.'''
        pass

    def slice_fail_ultimate(self,
            incisor: slcgen((object, object, object)),
            ):
        '''The ultimate fallback for unrecognised slice types.'''
        pass

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.slcgetmeths = _TypeMap(cls._yield_getmeths('slice_'))



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