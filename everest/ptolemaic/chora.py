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
from enum import Enum as _Enum
from collections import abc as _collabc

from everest.utilities import (
    TypeMap as _TypeMap,
    caching as _caching,
    NotNone, Null, NoneType, EllipsisType, NotImplementedType,
    ObjectMask as _ObjectMask,
    reseed as _reseed,
    )
from everest.utilities.classtools import add_defer_meth as _add_defer_meth

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    IncisionHandler as _IncisionHandler,
    )
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ousia import Monument as _Monument
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.protean import Protean as _Protean


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


class Choric(metaclass=_abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if not issubclass(ACls, _Incisable):
            return NotImplemented
        for Base in ACls.__mro__:
            if 'Chora' in Base.__dict__:
                return True
        return NotImplemented


class ElementType(_Enum):

    GENERIC = '__incise_generic__'
    VARIABLE = '__incise_variable__'
    DEFAULT = '__incise_default__'

    @classmethod
    def complies(cls, ACls, /):
        for meth in cls:
            name = meth.value
            for Base in ACls.__mro__:
                if name in Base.__dict__:
                    break
            else:
                return False
        return True

    def __call__(self, on: _collabc.Callable, /):
        try:
            return getattr(on, self.value)
        except AttributeError as exc:
            raise TypeError(
                f"Element type {self} not supported "
                f"on object {on} of type {type(on)}."
                ) from exc


class ChoraMeta(_Essence):
    ...


class Chora(_Incisable, metaclass=ChoraMeta):

    MERGETUPLES = ('PREFIXES', 'REQMETHS')
    PREFIXES = (
        'handle',
        *(protocol.name.lower() for protocol in _IncisionProtocol),
        )
    REQMETHS = (
        *(el.value for el in ElementType),
#         'retrievable', 'slyceable', 'iselement',
        )

    def handle_none(self, incisor: type(None), /, *, caller):
        return ElementType.DEFAULT(caller)()

    def handle_elementtype(self, incisor: ElementType, /, *, caller):
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

    @classmethod
    def incise(cls, user, arg, /, *, caller: _IncisionHandler):
        return cls.getmeths[type(arg)](user, arg, caller=caller)

    def __incise__(self, incisor, /, *, caller: _IncisionHandler):
        return self.Chora.incise(self, incisor, caller=caller)

    def __incise_generic__(self, /):
        return Generic(self)

    def __incise_variable__(self, /):
        return Variable(self)

    def __incise_default__(self, /):
        raise NotImplementedError

    @classmethod
    def compatible(cls, ACls, /):
        return isinstance(ACls, _Essence)

    @classmethod
    def __class_call__(cls, ACls: _Essence, /):
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
        if isinstance(type(ACls), Chora):
            chora = ACls
        elif hasattr(ACls, 'Chora'):
            chora = ACls.Chora
        else:
            return NotImplemented
        return cls in chora.__mro__


class Universal(Chora):

    def incise_chora(self, incisor: Chora, /):
        return incisor

    def retrieve_object(self, incisor: object, /):
        return incisor


@Universal
class Universe(_Monument):
    ...


UNIVERSE = Universe()


class Element(metaclass=_Essence):

    ...


class Generic(Element, metaclass=_Eidos):

    FIELDS = (
        _inspect.Parameter('basis', 0, default=UNIVERSE),
        _inspect.Parameter('identity', 3, default=None),
        )

    reseed = _reseed.GLOBALRAND

    @classmethod
    def parameterise(cls, cache, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        if (argu := bound.arguments)['identity'] is None:
            argu['identity'] = cls.reseed.rdigits(12)
        return bound


class Variable(Element, metaclass=_Protean):

    defaultbasis = UNIVERSE

    _var_slots__ = ('value', '_value')

    @property
    def value(self, /):
        try:
            return self._value
        except AttributeError as exc:
            raise ValueError from exc

    @value.setter
    def value(self, val, /):
        if val in self.basis:
            self._alt_setattr__('_value', val)
        else:
            raise ValueError(val)

    @value.deleter
    def value(self, /):
        self._alt_delattr__('_value')


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


@Chora
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
