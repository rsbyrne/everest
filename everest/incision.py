###############################################################################
''''''
###############################################################################


import abc as _abc
from enum import Enum as _Enum
from collections import deque as _deque
from collections import abc as _collabc
import inspect as _inspect

from everest import epitaph as _epitaph
from everest.utilities import Null as _Null
# from everest.utilities import reseed as _reseed

# from everest.ptolemaic.eidos import Eidos as _Eidos

from everest.exceptions import (
    IncisionException,
    IncisorTypeException,
    )


class IncisionProtocol(_Enum):

    TRIVIAL = '__incise_trivial__'
    SLYCE = '__incise_slyce__'
    RETRIEVE = '__incise_retrieve__'
    FAIL = '__incise_fail__'

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
                f"Incision protocol {self} not supported "
                f"on object {on} of type {type(on)}."
                ) from exc


class IncisionHandler(_abc.ABC):

    __slots__ = ()

    def __incise_trivial__(self, /):
        return self

    def __incise_slyce__(self, incisor, /):
        return incisor

    def __incise_retrieve__(self, incisor, /) -> _Null:
        return incisor

    def __incise_fail__(self, incisor, message, /):
        raise IncisorTypeException(incisor, self, message)

    @classmethod
    def __subclasshook__(cls, ACls):
        if cls is not IncisionHandler:
            return NotImplemented
        return IncisionProtocol.complies(ACls)


class ChainIncisionHandler(IncisionHandler, _deque):

    __slots__ = ()

    def __incise_trivial__(self, chora, /):
        return self[0]

    def __incise_slyce__(self, chora, /):
        for obj in reversed(self):
            chora = obj.__incise_slyce__(chora)
        return chora

    def __incise_retrieve__(self, index, /):
        for obj in reversed(self):
            index = obj.__incise_retrieve__(index)
        return index


class Incisable(IncisionHandler):

    __slots__ = ()

    REQMETHS = (
        '__getitem__', '__contains__', '__incise__', '__chain_incise__',
        *(protocol.value for protocol in IncisionProtocol),
        )

    @_abc.abstractmethod
    def __incise__(self, incisor, /, *, caller: IncisionHandler):
        raise NotImplementedError

    def __chain_incise__(self, incisor, /, *, caller: IncisionHandler):
        if isinstance(caller, ChainIncisionHandler):
            caller.append(self)
        else:
            caller = ChainIncisionHandler((caller, self))
        return self.__incise__(incisor, caller=caller)

    def __getitem__(self, arg, /):
        return self.__incise__(arg, caller=self)

    def __contains__(self, arg, /):
        try:
            rettyp = self.__incise_retrieve__.__annotations__['return']
        except KeyError:
            raise NotImplementedError
        return isinstance(arg, rettyp)

    @classmethod
    def __subclasshook__(cls, ACls, /):
        if cls is not Incisable:
            return NotImplemented
        for name in cls.REQMETHS:
            for Base in ACls.__mro__:
                if name in Base.__dict__:
                    break
            else:
                return False
        return True


class Degenerate(Incisable):

    __slots__ = ('value', '_epitaph')

    def __init__(self, value, /):
        self.value = value

    def __incise__(self, incisor, /, *, caller):
        return caller.fail(self, incisor)

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


###############################################################################
###############################################################################
