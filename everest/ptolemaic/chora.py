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

from everest import ur as _ur
from everest.utilities import (
    TypeMap as _TypeMap, FrozenMap as _FrozenMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType, NotImplementedType,
    )
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    IncisionHandler as _IncisionHandler,
    ChainIncisable as _ChainIncisable,
    )
from everest.epitaph import Epitaph as _Epitaph

from everest.ptolemaic.pleroma import Pleroma as _Pleroma
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia


class ChoretDescriptor:

    __slots__ = ('Choret',)

    def __init__(self, choret, /):
        self.Choret = choret

    def __get__(self, instance, owner=None, /):
        return self.Choret(instance)

    @property
    def __mroclass_basis__(self, /):
        return self.Choret


class ChoretMeta(_Sprite):

    def __set_name__(cls, owner, name, /):
        if not isinstance(owner, _Essence):
            return
        if name != '__incision_manager__':
            return
        cls.decorate(owner)

    descriptor = property(ChoretDescriptor)


class Choret(metaclass=ChoretMeta):

    BOUNDREQS = ()

    bound: object

    @classmethod
    def __class_init__(cls, /):
        pass

    @classmethod
    def compatible(cls, ACls, /):
        if not isinstance(ACls, _Essence):
            return False
        return True

    @classmethod
    def decorate(cls, ACls, /):
        if not cls.compatible(ACls):
            raise TypeError(f"Type {ACls} incompatible with chora {cls}.")
        if hasattr(cls, '__choret_decorate__'):
            ACls.__choret_decorate__(cls)
            return ACls
        with ACls.mutable:
            setattr(ACls, '__incision_manager__', cls.descriptor)
            if not '__getitem__' in dir(ACls):
                setattr(ACls, '__getitem__', _Incisable.__getitem__)
            ACls._ptolemaic_choret_decorated_ = True
        return ACls

    @_abc.abstractmethod
    def __incise__(self, *_, **__):
        raise NotImplementedError


#     @classmethod
#     def __subclasshook__(cls, ACls, /):
#         if issubclass(ACls, Chora):
#             return issubclass(ACls.Choret, cls)
#         return super().__subclasshook__(ACls)


class Chora(_IncisionHandler, metaclass=_Essence):
    '''The `Chora` type is the Ptolemaic implementation '''
    '''of the Everest 'incision protocol'. '''
    '''`Chora` objects can be thought of as representing 'space' '''
    '''in both concrete and abstract ways.'''

    MROCLASSES = ('__incision_manager__',)

    __incision_manager__ = Choret

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if cls is Chora:
            if isinstance(ACls, (_Essence, _Pleroma)):
                if issubclass(ACls, _Incisable):
                    return True
            return False
        return super().__subclasshook__(ACls)

#     @classmethod
#     def __init_subclass__(cls, /, *_, **__):
#         raise TypeError("This class cannot be subclassed.")

_Incisable.register(Chora)


def _wrap_trivial(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, _, /, *, caller):
        return _IncisionProtocol.TRIVIAL(caller)
    return wrapper

def _wrap_slyce(meth, /):
    @_functools.wraps(meth)
    def wrapper(self, arg, /, *, caller):
        return _IncisionProtocol.SLYCE(caller)(meth(self, arg))
    return wrapper

def _wrap_compose(meth, /):
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

URPROTOCOLS = {
    _ur.Var: _IncisionProtocol.VARIABLE,
    _ur.Dat: _IncisionProtocol.GENERIC,
    }


class Basic(Choret):

    MERGETUPLES = ('PREFIXES', 'BOUNDREQS')
    PREFIXES = ('handle', *WRAPMETHS)

    @property
    def __getitem__(self, /):
        raise NotImplementedError

    def handle_none(self, incisor: type(None), /, *, caller):
        return _IncisionProtocol.GENERIC(caller)

#     def handle_protocol(self, incisor: _IncisionProtocol, /, *, caller):
#         return incisor(caller)()

    def handle_ur(self, incisor: _ur.Ur, /, *, caller):
        return URPROTOCOLS[incisor](caller)

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
                hint = meth.__annotations__.get('incisor', cls)
                if isinstance(hint, str):
                    if hint.startswith('.'):
                        attrnames = iter(hint.strip('.').split('.'))
                        hint = cls
                        for attrname in attrnames:
                            hint = getattr(hint, attrname)
                    else:
                        hint = eval(hint)
                elif isinstance(hint, _Epitaph):
                    hint = hint.decode()
                hint = hintprocess(hint)
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


class Degenerate(_Incisable, metaclass=_Sprite):

    value: object

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
        return self.value.__eq__


class Degenerator(_ChainIncisable, metaclass=_Sprite):

    chora: Chora

    @property
    def __incision_manager__(self, /):
        return self.chora

    @property
    def __incise_retrieve__(self, /):
        return _IncisionProtocol.DEGENERATE(self.chora, Degenerate)


class Multi(Basic):

    @property
    def choras(self, /):
        return self.bound.choras

    @property
    def IsoForm(self, /):
        return self.bound.IsoForm

    @property
    def AnisoForm(self, /):
        return self.bound.AnisoForm

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
                    yield Degenerator(chora)[incisor]
                    break
        except StopIteration:
            raise ValueError("Too many incisors in tuple incision.")
        yield from chorait


class MultiTuple(Multi):

#     BOUNDREQS = ('choras',)

    def handle_tuple(self, incisor: tuple, /, *, caller):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        if not incisor:
            return _IncisionProtocol.TRIVIAL(caller)
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            incisor = tuple(cho.value for cho in choras)
            return _IncisionProtocol.RETRIEVE(caller)(incisor)
        return _IncisionProtocol.SLYCE(caller)(self.slyce_tuple(choras))

    def slyce_tuple(self, incisor: tuple, /):
        # Invisible to getmeths!
        if len(set(incisor)) == 1:
            return self.IsoForm(incisor[0], len(incisor))
        return self.AnisoForm(incisor)

    def __contains__(self, arg: tuple, /):
        if len(arg) > len(self.choras):
            return False
        for val, chora in zip(arg, self.choras):
            if val not in chora:
                return False
        return True


class MultiDict(Multi):

    @property
    def choras(self, /):
        return tuple(self.bound.choras.values())

    @property
    def chorakws(self, /):
        return self.bound.choras

    def handle_tuple(self, incisor: tuple, /, *, caller):
        '''Captures the special behaviour implied by `self[a,b,...]`'''
        if not incisor:
            return _IncisionProtocol.TRIVIAL(caller)
        choras = tuple(self.yield_tuple_multiincise(*incisor))
        if all(isinstance(cho, Degenerate) for cho in choras):
            incisor = _FrozenMap(zip(
                self.chorakws,
                (cho.value for cho in choras),
                ))
            return _IncisionProtocol.RETRIEVE(caller)(incisor)
        incisor = _FrozenMap(zip(self.chorakws, choras))
        return _IncisionProtocol.SLYCE(caller)(self.slyce_dict(incisor))

    def yield_dict_multiincise(self, /, **incisors):
        chorakws = self.chorakws
        for name, incisor in incisors.items():
            chora = chorakws[name]
            yield name, _IncisionProtocol.INCISE(chora)(
                incisor, caller=Degenerator(chora)
                )

    def handle_dict(self, incisor: dict, /, *, caller):
        if not incisor:
            return _IncisionProtocol.TRIVIAL(caller)
        choras = (
            self.chorakws
            | dict(self.yield_dict_multiincise(**incisor))
            )
        if all(
                isinstance(chora, Degenerate)
                for chora in choras.values()
                ):
            incisor = _FrozenMap({
                key: val.value for key, val in choras.items()
                })
            return _IncisionProtocol.RETRIEVE(caller)(incisor)
        return _IncisionProtocol.SLYCE(caller)(self.slyce_dict(incisor))

    def slyce_dict(self, incisor: dict, /):
        # Invisible to getmeths!
        choras = tuple(incisor.values())
        if len(set(choras)) == 1:
            return self.IsoForm(choras[0], tuple(incisor.keys()))
        return self.AnisoForm(incisors)

    def __contains__(self, arg: dict, /):
        choras = self.chorakws
        if len(arg) > len(choras):
            return False
        for key, val in arg.items():
            try:
                chora = choras[key]
            except KeyError:
                return False
            if val not in chora:
                return False
        return True


###############################################################################
###############################################################################


#         for methname in ('__incise__', '__contains__'):
#             if hasattr(cls, methname):
#                 exec('\n'.join((
#                     f"@property",
#                     f"def {methname}(self, /):",
#                     f"    return self.Choret(self).{methname}",
#                     )))
#                 decoratemeths[methname] = eval(methname)

#         if not issubclass(ACls, _IncisionHandler):
#             return False
#         direc = dir(ACls)
#         slots = getattr(ACls, '_req_slots__', ())
#         fields = getattr(ACls, 'fields', ())
#         for name in cls.BOUNDREQS:
#             if name not in direc:
#                 if name not in slots:
#                     if name not in fields:
#                         return False


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