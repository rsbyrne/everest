###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import deque as _deque
from collections import abc as _collabc
import inspect as _inspect
import collections as _collections

from everest import epitaph as _epitaph
from everest.utilities import Null as _Null
from everest.utilities.protocol import Protocol as _Protocol
# from everest.utilities import reseed as _reseed

# from everest.ptolemaic.eidos import Eidos as _Eidos

from everest.exceptions import (
    IncisionException,
    IncisorTypeException,
    IncisionProtocolException,
    )


class IncisionProtocol(_Protocol):

    # Mandatory:
    INCISE = ('__incise__', True)
    TRIVIAL = ('__incise_trivial__', True)
    SLYCE = ('__incise_slyce__', True)
    RETRIEVE = ('__incise_retrieve__', True)
    FAIL = ('__incise_fail__', True)

    # Optional:

    GENERIC = ('__incise_generic__', False)
    VARIABLE = ('__incise_variable__', False)
    DEGENERATE = ('__incise_degenerate__', False)
#     CONTAINS = '__contains__'
#     LEN = '__len__'
#     ITER = '__iter__'

    @classmethod
    def defer(cls, obj, /):
        return getattr(obj, '__incision_manager__')

    def exc(self, obj, /):
        return IncisionProtocolException(self, obj)


class IncisionHandler(metaclass=_abc.ABCMeta):

    __slots__ = ()

    @property
    def __incise_trivial__(self, /):
        return self

    def __incise_retrieve__(self, incisor, /):
        return incisor

    def __incise_slyce__(self, incisor, /):
        return incisor

    def __incise_fail__(self, incisor, message=None, /):
        if isinstance(message, Exception):
            raise IncisorTypeException(incisor, self) from message
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


class PseudoIncisable(metaclass=_abc.ABCMeta):

    __slots__ = ()

    @_abc.abstractmethod
    def __incise__(self, incisor, /, *, caller):
        raise NotImplementedError

    def __getitem__(self, arg, /):
        return IncisionProtocol.INCISE(self)(arg, caller=self)


class Incisable(IncisionHandler, PseudoIncisable):

    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if cls is Incisable:
            return IncisionProtocol.complies(ACls)
        return super().__subclasshook__(ACls)


class IncisionChain(Incisable):

    __slots__ = ('incisables',)

    def __init__(self, incisables: tuple, /):
        self.incisables = tuple(incisables)

    def __incise__(self, incisor, /, *, caller):
        return IncisionProtocol.INCISE(self.incisables[0])(
            incisor, caller=caller
            )

    @property
    def __incise_trivial__(self, /):
        return IncisionProtocol.TRIVIAL(self.incisables[-1])

    def __incise_slyce__(self, incisor, /):
        for obj in self.incisables:
            incisor = IncisionProtocol.SLYCE(obj)(incisor)
        return incisor

    def __incise_retrieve__(self, incisor, /):
        for obj in self.incisables:
            incisor = IncisionProtocol.RETRIEVE(obj)(incisor)
        return incisor

    def __incise_degenerate__(self, incisor, /):
        *members, last = self.incisables
        for obj in members:
            incisor = IncisionProtocol.RETRIEVE(obj)(incisor)
        return IncisionProtocol.DEGENERATE(last)(incisor)

    @property
    def __incise_fail__(self, /):
        return IncisionProtocol.FAIL(self.incisables[-1])

    def __repr__(self, /):
        return f"{type(self)}{self.incisables}"


class ChainIncisable(Incisable):

    __slots__ = ()

    @property
    @_abc.abstractmethod
    def __incision_manager__(self, /) -> Incisable:
        raise NotImplementedError

    def __incise__(self, incisor, /, *, caller):
        return IncisionProtocol.INCISE(man := self.__incision_manager__)(
            incisor,
            caller=IncisionChain((man, caller))
            )


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
