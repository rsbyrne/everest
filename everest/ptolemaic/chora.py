###############################################################################
''''''
###############################################################################


import functools as _functools
import operator as _operator
from collections import deque as _deque, abc as _collabc
import typing as _typing
import types as _types
import itertools as _itertools
import abc as _abc
import weakref as _weakref
from dataclasses import dataclass as _dataclass

# from everest import ur as _ur
from everest.utilities import (
    TypeMap as _TypeMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType, NotImplementedType,
    )
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    PseudoIncisable as _PseudoIncisable,
    IncisionHandler as _IncisionHandler,
    ChainIncisable as _ChainIncisable,
    )
from everest.epitaph import Epitaph as _Epitaph

from everest.ptolemaic.armature import ArmatureProtocol as _ArmatureProtocol
from everest.ptolemaic.diict import Kwargs as _Kwargs
from everest.ptolemaic.pleroma import Pleroma as _Pleroma
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic import query as _query


class Gen(metaclass=_Sprite):
    ...


class Var(metaclass=_Protean):

    _req_slots__ = ('_value',)
    _var_slots__ = ('value',)

    _default = None

    @property
    def value(self, /):
        try:
            return self._value
        except AttributeError:
            val = self._default
            self._alt_setattr__('_value', val)
            return val

    @value.setter
    def value(self, val, /):
        if val not in self.basis:
            raise ValueError(val)
        self._alt_setattr__('_value', val)

    @value.deleter
    def value(self, /):
        self._alt_setattr__('_value', self._default)


class Empty(_Incisable, metaclass=_Sprite):

    chora: _Incisable

    def __incise__(self, incisor, /, *, caller):
        return _IncisionProtocol.FAIL(caller)(
            incisor,
            "Cannot further incise an empty incisable."
            )

    @property
    def __getitem__(self, /):
        raise ValueError("Cannot incise a degenerate.")

    def __contains__(self, _, /):
        return False


class Degenerate(_Incisable, metaclass=_Sprite):

    arg: object

    def retrieve(self, /):
        return self.arg

#     @property
#     @_abstractmethod
#     def value(self, /) -> object:
#         raise NotImplementedError

    def __incise__(self, incisor, /, *, caller):
        return _IncisionProtocol.FAIL(caller)(
            incisor,
            "Cannot further incise an already degenerate incisable."
            )

    @property
    def __getitem__(self, /):
        raise ValueError("Cannot incise a degenerate.")

    @property
    def __contains__(self, /):
        return self.retrieve().__eq__


# @_Incisable.register
class Chora(_PseudoIncisable, metaclass=_Essence):
    '''The `Chora` type is the Ptolemaic implementation '''
    '''of the Everest 'incision protocol'. '''
    '''`Chora` objects can be thought of as representing 'space' '''
    '''in both concrete and abstract ways.'''

    MROCLASSES = ('Gen', 'Var', 'Empty', 'Degenerate')

    Gen, Var, Empty, Degenerate = Gen, Var, Empty, Degenerate

    def __incise_empty__(self, /):
        return Empty(self)

    @property
    def __incise_degenerate__(self, /):
        return self.Degenerate

    @property
    def __armature_generic__(self, /):
        return self.Gen

    @property
    def __armature_variable__(self, /):
        return self.Var

    @property
    def __contains__(self, /):
        return _IncisionProtocol.CONTAINS(self)

    @property
    def __len__(self, /):
        return _IncisionProtocol.LENGTH(self)

    @property
    def __iter__(self, /):
        return _IncisionProtocol.ITER(self)

    @property
    def __includes__(self, /):
        return _IncisionProtocol.INCLUDES(self)

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if cls is Chora:
            if isinstance(ACls, (_Essence, _Pleroma)):
                if issubclass(ACls, _Incisable):
                    return True
            return False
        return super().__subclasshook__(ACls)


class Degenerator(_ChainIncisable, metaclass=_Sprite):

    chora: Chora

    @property
    def __incision_manager__(self, /):
        return self.chora

    @property
    def __incise_retrieve__(self, /):
        return _IncisionProtocol.DEGENERATE(self.chora)


class ChainChora(Chora, _ChainIncisable):
    ...


class Choret(metaclass=_Sprite):

    BOUNDREQS = ()

    bound: object

    def __incise__(self, incisor, /, *, caller):
        return _IncisionProtocol.FAIL(caller)(incisor)


class Choric(Chora, _Incisable, metaclass=_Essence):

    MROCLASSES = ('__choret__',)

    __choret__ = Choret

    @property
    @_caching.soft_cache()  # Will create a circular reference!
    def __incision_manager__(self, /):
        return self.__choret__(self)

    @property
    def __incise__(self, /):
        return self.__incision_manager__.__incise__


class TrivialException(Exception):
    ...


def _wrap_trivial(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, _, /, *, caller):
        return _IncisionProtocol.TRIVIAL(caller)()
    return wrapper

def _wrap_slyce(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        try:
            result = meth(self, arg)
        except TrivialException:
            return _IncisionProtocol.TRIVIAL(caller)()
        except Exception as exc:
            return _IncisionProtocol.FAIL(caller)(arg, exc)
        return _IncisionProtocol.SLYCE(caller)(result)
    return wrapper

# def _wrap_compose(meth, /):
#     @_functools.wraps(meth)
#     def wrapper(self, arg, /, *, caller):
#         return _IncisionProtocol.SLYCE(caller)(meth(self, arg))
#     return wrapper

def _wrap_retrieve(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        try:
            result = meth(self, arg)
        except TrivialException:
            return _IncisionProtocol.TRIVIAL(caller)()
        except Exception as exc:
            return _IncisionProtocol.FAIL(caller)(arg, exc)
        return _IncisionProtocol.RETRIEVE(caller)(result)
    return wrapper

def _wrap_fail(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        try:
            result = meth(self, arg)
        except TrivialException:
            return _IncisionProtocol.TRIVIAL(caller)()
        except Exception as exc:
            return _IncisionProtocol.FAIL(caller)(arg, exc)
        return _IncisionProtocol.FAIL(caller)(arg, result)
    return wrapper

WRAPMETHS = dict(
    trivial=_wrap_trivial,
    slyce=_wrap_slyce,
    retrieve=_wrap_retrieve,
    fail=_wrap_fail,
    )

# URPROTOCOLS = {
#     _ur.Var: _ArmatureProtocol.VARIABLE,
#     _ur.Dat: _ArmatureProtocol.GENERIC,
#     }


class Basic(Choret):

    MERGETUPLES = ('PREFIXES', 'BOUNDREQS')
    PREFIXES = ('handle', *WRAPMETHS)

    @property
    def __getitem__(self, /):
        raise NotImplementedError

#     def handle_none(self, incisor: type(None), /, *, caller):
#         return _IncisionProtocol.GENERIC(caller)

#     def handle_protocol(self, incisor: _IncisionProtocol, /, *, caller):
#         return incisor(caller)()

    # def handle_ur(self, incisor: _ur.Ur, /, *, caller):
    #     return URPROTOCOLS[incisor](caller)

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
    def process_hint(cls, hint, /):
        if isinstance(hint, str):
            try:
                return _operator.attrgetter(hint)(cls)
            except AttributeError:
                return Null
        if isinstance(hint, tuple):
            return tuple(map(cls.process_hint, hint))
        if isinstance(hint, _Epitaph):
            return cls.process_hint(hint.decode())
        return hint

    @classmethod
    def process_multihint(cls, hint, /):
        return tuple[cls.process_hint(hint)]

    @classmethod
    def _yield_getmeths(cls, /,
            preprefix='', defaultwrap=(lambda x: x),
            hintprocess=None, 
            ):
        if hintprocess is None:
            hintprocess = cls.process_hint
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


class Composition(_Incisable, metaclass=_Sprite):

    fobj: Chora
    gobj: Chora

    @property
    def __incise__(self, /):
        return _IncisionProtocol.INCISE(self.gobj)

    def __incise_trivial__(self, /):
        return self

    def __incise_slyce__(self, incisor, /):
        return type(self)(
            self.fobj,
            _IncisionProtocol.SLYCE(self.gobj)(incisor),
            )

    def __incise_retrieve__(self, incisor, /):
        return self.fobj[
            _IncisionProtocol.RETRIEVE(self.gobj)(incisor)
            ]


class Composable(Basic):

    def slyce_compose(self, incisor: _Incisable, /):
        '''Returns the composition of two choras, i.e. f(g(x)).'''
        return Composition(self.bound, incisor)


class Sliceable(Basic):

    def handle_slice(self, incisor: slice, /, *, caller):
        return self.slicegetmeths[
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
        cls.slicegetmeths = _TypeMap(cls._yield_getmeths(
            'slice',
            hintprocess=cls.process_multihint,
            ))


class Sampleable(Basic):

    def handle_slice(self, incisor: slice, /, *, caller):
        return (
            caller
            [_query.Bounds(incisor.start, incisor.stop)]
            [_query.Sample(incisor.step)]
            )

    def handle_bounds(self, incisor: _query.Bounds, /, *, caller):
        return self.boundsgetmeths[type(incisor.lower), type(incisor.upper)](
            self, incisor, caller=caller
            )

    def bounds_trivial_none(self, incisor: (type(None), type(None)), /):
        pass

    def bounds_fail_ultimate(self, incisor: (object, object), /):
        pass

    def handle_sample(self, incisor: _query.Sample, /, *, caller):
        incisor = incisor.content
        return self.samplegetmeths[type(incisor)](
            self, incisor, caller=caller
            )

    def sample_trivial_none(self, incisor: type(None), /):
        pass

    def sample_fail_ultimate(self, incisor: object, /):
        pass

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.update_getmeth_names('bounds')
        cls.boundsgetmeths = _TypeMap(cls._yield_getmeths(
            'bounds',
            hintprocess=cls.process_multihint,
            ))
        cls.update_getmeth_names('sample')
        cls.samplegetmeths = _TypeMap(cls._yield_getmeths('sample'))


class Multi(Basic):

    @property
    def labels(self, /):
        return self.bound.keys()

    @property
    def choras(self, /):
        return self.bound.values()

    @property
    def depth(self, /):
        return len(self.choras)

    @property
    @_caching.soft_cache()
    def active(self, /):
        return tuple(
            not isinstance(cho, Degenerate) for cho in self.choras
            )

    @property
    @_caching.soft_cache()
    def activechoras(self, /):
        return tuple(_itertools.compress(self.choras, self.active))

    @property
    def activedepth(self, /):
        return len(self.activechoras)

    @property
    def degenerate(self, /):
        return self.activedepth <= 1

    def _handle_generic(self, incisor, /, *, caller, meth):
        choras = tuple(meth(incisor))
        if all(isinstance(chora, Degenerate) for chora in choras):
            return _IncisionProtocol.RETRIEVE(caller)(tuple(
                chora.retrieve() for chora in choras
                ))
        if len(set(choras)) == 1:
            slyce = self.bound.SymForm(choras[0], self.labels, self.depth)
        else:
            slyce = self.bound.AsymForm(choras, self.labels)
        return _IncisionProtocol.SLYCE(caller)(slyce)

    def yield_mapping_multiincise(self, incisors: _collabc.Mapping, /):
        choras, keys = self.choras, self.labels
        for key, chora in zip(keys, choras):
            if key in incisors:
                yield _IncisionProtocol.INCISE(chora)(
                    incisors[key], caller=Degenerator(chora)
                    )
            else:
                yield chora

    def yield_single_multiincise(self, incisor, /):
        chorait = iter(self.choras)
        while True:
            chora = next(chorait)
            if isinstance(chora, Degenerate):
                yield chora
            else:
                yield Degenerator(chora)[incisor]
                break
        else:
            assert False
        yield from chorait

    def yield_sequence_multiincise(self, incisors: _collabc.Sequence, /):
        ncho = self.activedepth
        ninc = len(incisors)
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
                    yield Degenerator(chora)[incisor]
                    break
        except StopIteration:
            raise ValueError("Too many incisors in tuple incision.")
        yield from chorait

    def handle_mapping(self, incisor: _Kwargs, /, *, caller, shallow=False):
        if not incisor:
            return _IncisionProtocol.TRIVIAL(caller)()
        if shallow:
            meth = self.yield_mapping_multiincise
        elif self.activedepth == 1:
            meth = self.yield_single_multiincise
        else:
            meth = self.yield_mapping_multiincise
        return self._handle_generic(incisor, caller=caller, meth=meth)

    def handle_sequence(self, incisor: tuple, /, *, caller, shallow=False):
        if not incisor:
            return _IncisionProtocol.TRIVIAL(caller)()
        if shallow:
            meth = self.yield_sequence_multiincise
        elif self.activedepth == 1:
            meth = self.yield_single_multiincise
        else:
            meth = self.yield_sequence_multiincise
        return self._handle_generic(incisor, caller=caller, meth=meth)

    def handle_shallow(self, incisor: _query.Shallow, /, *, caller):
        incisor = incisor.query
        return self.getmeths[type(incisor)](self,
            incisor, caller=caller, shallow=True
            )

    def handle_other(self, incisor: object, /, *, caller):
        meth = self.yield_single_multiincise
        return self._handle_generic(incisor, caller=caller, meth=meth)

    def __incise_contains__(self, arg, /):
        choras = self.choras
        if len(arg) > len(choras):
            return False
        elif isinstance(arg, _collabc.Mapping):
            for key, chora in zip(self.labels, choras):
                if key in arg:
                    if arg[key] not in chora:
                        return False
        else:
            for val, chora in zip(arg, self.choras):
                if val not in chora:
                    return False
        return True


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