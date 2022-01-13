###############################################################################
''''''
###############################################################################


import abc as _abc
from enum import EnumMeta as _EnumMeta, Enum as _Enum
from collections import deque as _deque
from collections import abc as _collabc
import inspect as _inspect
import weakref as _weakref
import collections as _collections

from everest import epitaph as _epitaph
from everest.utilities import Null as _Null
# from everest.utilities import reseed as _reseed

# from everest.ptolemaic.eidos import Eidos as _Eidos

from everest.exceptions import (
    IncisionException,
    IncisorTypeException,
    IncisionProtocolException,
    )


class _IncisionProtocolMeta_(_EnumMeta):

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._compliant = _weakref.WeakKeyDictionary()
        cls.DEFER = '__defer_incise__'
        cls.mandatory = tuple(
            cls[name].value for name in ('INCISE',)
            )


class IncisionProtocol(_Enum, metaclass=_IncisionProtocolMeta_):

    # Mandatory:
    INCISE = '__incise__'
    TRIVIAL = '__incise_trivial__'
    RETRIEVE = '__incise_retrieve__'
    SLYCE = '__incise_slyce__'
    FAIL = '__incise_fail__'

    # Optional:

    GENERIC = '__incise_generic__'
    VARIABLE = '__incise_variable__'

    @classmethod
    def defer(cls, obj, /):
        return getattr(obj, cls.DEFER)

    @classmethod
    def complies(cls, ACls, /):
        compliant = cls._compliant
        try:
            return compliant[ACls]
        except KeyError:
            pass
        fallbackname = cls.DEFER
        if hasattr(ACls, fallbackname):
            out = compliant[ACls] = True
            return out
        for methodname in cls.mandatory:
            for Base in ACls.__mro__:
                dct = Base.__dict__
                if methodname in dct:
                    break
                if '__slots__' in dct:
                    slots = dct['__slots__']
                    if methodname in slots:
                        break
            else:
                out = compliant[ACls] = False
                return out
        out = compliant[ACls] = True
        return out

    @classmethod
    def decorate(cls, ACls, /):
        if not cls.complies(ACls):
            raise TypeError(f"Class {ACls} does not comply with protocol {cls}.")
        ACls.__getitem__ = Incisable.__getitem__
        ACls.__chain_incise__ = Incisable.__chain_incise__
        Incisable.register(ACls)
        return ACls

    def __call__(self, obj, /):
        value = self.value
        try:
            return getattr(obj, value)
        except AttributeError:
            try:
                return getattr(self.defer(obj), value)
            except AttributeError:
                raise self.exc(obj)

    def exc(self, obj, /):
        return IncisionProtocolException(self, obj)


class IncisionHandler(metaclass=_abc.ABCMeta):

    __slots__ = ()

    def __incise_trivial__(self, /):
        return self

    def __incise_retrieve__(self, incisor, /):
        return incisor

    def __incise_slyce__(self, incisor, /):
        return incisor

    def __incise_fail__(self, incisor, message=None, /):
        raise IncisorTypeException(incisor, self, message)

    @classmethod
    def __subclasshook__(cls, ACls):
        if cls is not IncisionHandler:
            return super().__subclasshook__(ACls)
        return all(
            hasattr(ACls, methname)
            for methname in cls.__dict__
            if methname.startswith('__incise_')
            )


class Incisable(IncisionHandler, metaclass=_abc.ABCMeta):

    __slots__ = ()

    @_abc.abstractmethod
    def __incise__(self, incisor, /, *, caller):
        raise NotImplementedError

    def __getitem__(self, arg, /):
        return IncisionProtocol.INCISE(self)(arg, caller=self)

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if cls is Incisable:
            return IncisionProtocol.complies(ACls)
        return super().__subclasshook__(ACls)


class Chain(
        Incisable,
        _collections.namedtuple('_ChainIncisable_', ('outer', 'inner')),
        ):

    @property
    def __incise__(self, /):
        return self.inner.__incise__

    def __incise_trivial__(self, /):
        return self[0].__incise__trivial__()

    def __incise_slyce__(self, chora, /):
        for obj in reversed(self):
            chora = obj.__incise_slyce__(chora)
        return chora

    def __incise_retrieve__(self, index, /):
        for obj in reversed(self):
            index = obj.__incise_retrieve__(index)
        return index

    @property
    def __incise_fail__(self, /):
        return self[0].__incise_fail__


class ChainIncisable(Incisable):

    __slots__ = ()

    @property
    @_abc.abstractmethod
    def __defer_incise__(self, /) -> Incisable:
        raise NotImplementedError

    @property
    def __incise__(self, /):
        return Chain(self, self.__defer_incise__).__incise__


class Composition(
    Incisable,
    _collections.namedtuple('_ChainIncisable_', ('fobj', 'gobj')),
    ):

    @property
    def __incise__(self, /):
        return self.gobj

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


# class Incisable(IncisionHandler):

#     __slots__ = ()

#     REQMETHS = (
#         '__getitem__', '__contains__', '__incise__', '__chain_incise__',
#         *(protocol.value for protocol in IncisionProtocol),
#         )

#     @_abc.abstractmethod
#     def __incise__(self, incisor, /, *, caller: IncisionHandler):
#         raise NotImplementedError

#     def __chain_incise__(self, incisor, /, *, caller: IncisionHandler):
#         if isinstance(caller, ChainIncisionHandler):
#             caller.append(self)
#         else:
#             caller = ChainIncisionHandler((caller, self))
#         return self.__incise__(incisor, caller=caller)

#     def __getitem__(self, arg, /):
#         return self.__incise__(arg, caller=self)

#     def __contains__(self, arg, /):
#         try:
#             rettyp = self.__incise_retrieve__.__annotations__['return']
#         except KeyError:
#             raise NotImplementedError
#         return isinstance(arg, rettyp)

#     def issuperset(self, other, /):
#         raise NotImplementedError

#     def issubset(self, other, /):
#         raise NotImplementedError

#     @classmethod
#     def __subclasshook__(cls, ACls, /):
#         if cls is Incisable:
#             return IncisionProtocol.complies(ACls)
#         return super().__subclasshook__(ACls)


###############################################################################
###############################################################################


# class IncisionChain(IncisionHandler, tuple):

#     __slots__ = ()

#     @classmethod
#     def yield_args(cls, arg):
#         for sub in arg:
#             if sub is None:
#                 pass
#             elif isinstance(sub, cls):
#                 yield from sub
#             else:
#                 yield sub

#     def __new__(cls, arg, /):
#         return super().__new__(cls, cls.yield_args(arg))

#     def __incise_trivial__(self, /):
#         return self[0].__incise__trivial__()

#     def __incise_slyce__(self, chora, /):
#         for obj in reversed(self):
#             chora = obj.__incise_slyce__(chora)
#         return chora

#     def __incise_retrieve__(self, index, /):
#         for obj in reversed(self):
#             index = obj.__incise_retrieve__(index)
#         return index

#     @property
#     def __incise_fail__(self, /):
#         return self[0].__incise_fail__


# class Incision(Incisable, metaclass=_Eidos):

#     incised: Incisable
#     incisor: Incisable

#     @property
#     def retrieve(self, /):
#         return self.incised.retrieve

#     @property
#     def slyce(self, /):
#         return self.incised.slyce

#     def __getitem__(self, arg, /):
#         return _functools.partial(self.chora.__getitem__, caller=self.incised)


# class DefaultCaller:

#     __slots__ = ()

#     def __new__(self, /, *_, **__):
#         raise RuntimeError

#     @classmethod
#     def incise(cls, chora, /):
#         return chora

#     @classmethod
#     def retrieve(cls, index, /):
#         return index

#     @classmethod
#     def trivial(cls, chora, /):
#         return chora

#     @classmethod
#     def fail(cls, chora, incisor, /):
#         raise IncisorTypeException(incisor, chora, cls)


# class Element(metaclass=_Eidos):

#     incised


# class DatElement(Element):

#     index: _collabc.Hashable


# class ArbitraryElement(Element):

#     FIELDS = (_inspect.Parameter('identity', 3, annotation=int),)

#     @classmethod
#     def parameterise(cls, /,
#             cache, *args, identity=_reseed.GLOBALRAND, **kwargs
#             ):
#         if isinstance(identity, _reseed.Reseed):
#             identity = _reseed.rdigits(12, seed=identity)
#         return super().parameterise(
#             cache, *args, identity=identity, **kwargs
#             )


# class GenericElement(ArbitraryElement, metaclass=_Eidos):
#     ...


# class VarElement(ArbitraryElement, metaclass=_Eidos):
#     ...
