###############################################################################
''''''
###############################################################################


import abc as _abc
from enum import Enum as _Enum
from collections import deque as _deque
from collections import abc as _collabc
import inspect as _inspect

from everest import epitaph as _epitaph
from everest.utilities import reseed as _reseed

from everest.ptolemaic.eidos import Eidos as _Eidos

from everest.ptolemaic.exceptions import (
    IncisionException,
    IncisorTypeException,
    )


class IncisionProtocol(_Enum):

    TRIVIAL = 'trivial'
    INCISE = 'incise'
    GENERIC = 'generic'
    VARIABLE = 'variable'
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
        try:
            return getattr(on, self.value)
        except AttributeError as exc:
            raise TypeError(
                f"Incision protocol {self} not supported "
                f"on object {self} of type {type(self)}."
                ) from exc


class IncisionHandler(_abc.ABC):

    __slots__ = ()

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

    __slots__ = ()

    @_abc.abstractmethod
    def __getitem__(self, arg, /, *, caller=None):
        raise NotImplementedError


class ChainIncisionHandler(IncisionHandler, _deque):

    __slots__ = ()

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

    def __new__(self, /, *_, **__):
        raise RuntimeError

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

    __slots__ = ()

    def incise(self, chora, /):
        return Incision(self, chora)

    def generic(self, /):
        return GenericElement(self)

    def variable(self, /):
        return VarElement(self)

    def retrieve(self, index, /):
        raise DatElement(self, index)

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


class Element(metaclass=_Eidos):

    incised: Incisable


class DatElement(Element):

    index: _collabc.Hashable


class ArbitraryElement(Element):

    FIELDS = (_inspect.Parameter('identity', 3, annotation=int),)

    @classmethod
    def parameterise(cls, /,
            cache, *args, identity=_reseed.GLOBALRAND, **kwargs
            ):
        if isinstance(identity, _reseed.Reseed):
            identity = _reseed.rdigits(12, seed=identity)
        return super().parameterise(
            cache, *args, identity=identity, **kwargs
            )


class GenericElement(ArbitraryElement, metaclass=_Eidos):
    ...


class VarElement(ArbitraryElement, metaclass=_Eidos):
    ...


class Incision(Incisable, metaclass=_Eidos):

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


###############################################################################
###############################################################################
