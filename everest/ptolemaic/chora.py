###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import inspect as _inspect
import collections as _collections
import typing as _typing

from everest.utilities import (
    TypeMap as _TypeMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType,
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic.armature import Armature as _Armature
from everest.ptolemaic import exceptions as _exceptions


PROTOCOLMETHS = ('trivial', 'incise', 'retrieve', 'fail')


class ChoraException(_exceptions.PtolemaicException):

    __slots__ = ('chora',)

    def __init__(self, chora=None, /, *args):
        self.chora = chora
        super().__init__(*args)

    def message(self, /):
        yield from super().message()
        chora = self.chora
        if chora is None:
            yield 'within the Chora system'
        elif chora is not self.ptolemaic:
            yield ' '.join((
                f'within its associated Chora object, `{repr(chora)}`',
                f'of type `{repr(type(chora))}`,',
                ))


class IncisorTypeException(
            _exceptions.IncisionException,
            ChoraException,
            TypeError,
            ):

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


class Incision(_Armature):

    FIELDS = ('incised', 'chora')

    def incise(self, chora, /):
        return type(self)(self.incised, chora)

    def __getitem__(self, arg, /):
        return self.chora.getitem(self, arg)

    def __getattr__(self, arg, /):
        superget = super().__getattribute__
        try:
            return superget(arg)
        except AttributeError:
            return getattr(superget('incised'), arg)


class IncisionHandler(metaclass=_Essence):

    @_abc.abstractmethod
    def incise(self, chora):
        raise NotImplementedError

    @_abc.abstractmethod
    def retrieve(self, index, /):
        raise NotImplementedError

    @_abc.abstractmethod
    def trivial(self, /):
        raise NotImplementedError

    @_abc.abstractmethod
    def fail(self, chora, incisor, /):
        raise NotImplementedError


def default_getmeth(obj, caller, incisor, /):
    raise IncisorTypeException(incisor, obj, caller)


class ChoraBase(metaclass=_Essence):

    def incise(self, chora, /):
        return chora

    def retrieve(self, index, /):
        return index

    def trivial(self, /):
        return self

    def fail(self, chora, incisor, /):
        raise IncisorTypeException(incisor, chora, self)

    def __getitem__(self, arg, /):
        return self.getitem(self, arg)

    @_abc.abstractmethod
    def getitem(self, caller: IncisionHandler, arg, /):
        raise NotImplementedError

    @staticmethod
    def default_incise(self, chora, /):
        return Incision(self, chora)

    @staticmethod
    def default_trivial(self, /):
        return self

    @staticmethod
    def default_fail(self, chora, incisor, /):
        raise IncisorTypeException(incisor, chora, self)

    @classmethod
    def decorate(cls, other, /):

        with other.clsmutable:

            other.Chora = cls

            exec('\n'.join((
                f"def __getitem__(self, arg, /):",
                f"    return self.chora.getitem(self, arg)",
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
                    meth = getattr(cls, f"default_{methname}")
                    setattr(other, methname, meth)

        return other


class CompositionHandler(IncisionHandler, _Armature):

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

    def incise(self, chora):
        return super().incise(self.fchora.compose(chora))

    def retrieve(self, index, /):
        return self.fchora.getitem(self.caller, index)

    def fail(self, chora, incisor, /):
        caller, fchora, gchora = self.caller, self.fchora, self.gchora
        return fchora.getitem(
            SuperCompHandler(caller, fchora, gchora),
            incisor,
            )
        

class Composition(ChoraBase, _Armature):

    FIELDS = ('fchora', 'gchora')

    def getitem(self, caller, incisor: object, /):
        fchora, gchora = self.fchora, self.gchora
        return self.gchora.getitem(
            SubCompHandler(caller, fchora, gchora),
            incisor,
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


class Chora(ChoraBase, _Armature):

    MERGETUPLES = ('PREFIX', 'TOWRAP')

    PREFIXES = ('handle', *PROTOCOLMETHS)

    def compose(self, other, /):
        return Composition(self, other)

    def handle_tuple(self, caller, incisor: tuple, /):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        length = len(incisor)
        if length == 0:
            return caller
        arg0, *argn = incisor
        out = self.getitem(caller, arg0)
        if argn:
            raise NotImplementedError
        return out

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
    def _yield_getmeths(cls, /, preprefix='', defaultwrap=(lambda x: x)):
        prefixes = cls.PREFIXES
        methnames = {prefix: _collections.deque() for prefix in prefixes}
        adjprefixes = tuple(map(preprefix.__add__, prefixes))
        for name in cls.attributes:
            for prefix, deq in zip(adjprefixes, methnames.values()):
                if name.startswith(prefix):
                    if name is prefix:
                        continue
                    deq.append(name)
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

    def getitem(self, caller, arg, /):
        return self.getmeths[type(arg)](self, caller, arg)


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