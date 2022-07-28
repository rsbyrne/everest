###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import inspect as _inspect
import types as _types
import sys as _sys

from ..ptolemaic import ptolemaic as _ptolemaic
from ..ptolemaic.essence import Essence as _Essence
from ..ptolemaic.ousia import Ousia as _Ousia
from ..ptolemaic.enumm import Enumm as _Enumm
from ..ptolemaic.sprite import Sprite as _Sprite
from ..ptolemaic.system import System as _System
from ..ptolemaic.stele import Stele as _Stele_

from . import pseudotype as _pseudotype
from .algebraic import AlgebraicType as _AlgebraicType


class _Stele_(_Stele_):

    def __call__(self, arg, /):
        if arg is self:
            arg = Sett
        return convert(arg)

    def __initialise__(self, /):
        super().__initialise__()
        try:
            setts = self.Setts
        except AttributeError:
            pass
        else:
            with self.mutable:
                for enumm in setts.enumerators:
                    setattr(self, enumm.name, enumm)

    def __instancecheck__(self, arg, /):
        return isinstance(arg, Sett)

    def __subclasscheck__(self, arg, /):
        return issubclass(arg, Sett)

    @property
    def register(self, /):
        return self.Sett.register

    def __mro_entries__(self, bases, /):
        return (self.Sett,)


_stele_ = _Stele_.commence()


class SettError(RuntimeError):

    ...


def convert(arg, /):
    if isinstance(arg, Sett):
        return arg
    if arg is Sett:
        return Setts.POWER
    if isinstance(arg, type):
        if isinstance(arg, _types.GenericAlias):
            return SettBrace(*map(arg.__args__), typ=arg.__orign__)
        return TypeSett(arg)
    # if hasattr(arg, '__sett_convert__'):
    #     return arg.__sett_convert__()
    if arg is NotImplemented:
        return Setts.NULL
    if arg in (_inspect._empty, Ellipsis):
        return Setts.UNIVERSE
    if isinstance(arg, _collabc.Container):
        return ContainerSett(arg)
    if isinstance(arg, _types.FunctionType):
        return FuncSett(arg)
    raise TypeError(arg, type(arg))


class _Any_(metaclass=_Essence):

    @classmethod
    def __class_instancecheck__(cls, other, /):
        return True

    @classmethod
    def __subclasshook__(cls, other, /):
        if cls is _Any_:
            return True
        return NotImplemented

    @classmethod
    def __class_call__(cls, arg, /):
        return arg


class _Null_(metaclass=_Essence):

    @classmethod
    def __class_instancecheck__(cls, other, /):
        return False

    @classmethod
    def __subclasshook__(cls, other, /):
        if cls is _Null_:
            return False
        return NotImplemented


with _stele_.block:


    class _Sett_(metaclass=_AlgebraicType):


        class Base(metaclass=_Ousia):

            __slots__ = dict(_signaltype=None)

            # def __init__(self, /):
            #     super().__init__()
            #     self.

            @property
            def signaltype(self, /):
                try:
                    return object.__getattribute__(self, '_signaltype')
                except AttributeError:
                    typ = self.get_signaltype()
                    if typ is NotImplemented:
                        typ = _Null_
                    elif typ is Ellipsis:
                        typ = _Any_
                    elif isinstance(typ, Sett):
                        typ = typ.signaltype
                    object.__setattr__(self, '_signaltype', typ)
                    return typ

            def get_signaltype(self, /):
                return _Any_

            def _contains_(self, arg, /):
                return NotImplemented

            def __contains__(self, arg, /):
                if not isinstance(arg, self.signaltype):
                    return False
                out = self._contains_(arg)
                if out is NotImplemented:
                    try:
                        meth = arg.__constitutes__
                    except AttributeError:
                        raise SettError
                    out = meth(arg)
                return bool(out)

            def _includes_(self, arg, /):
                return NotImplemented

            def __includes__(self, arg, /):
                if arg is Setts.NULL:
                    return True
                if not isinstance(arg, Sett):
                    raise SettError
                if not issubclass(arg.signaltype, self.signaltype):
                    return False
                out = self._includes_(arg)
                if out is NotImplemented:
                    try:
                        meth = arg.__entails__
                    except AttributeError:
                        raise SettError
                    out = meth(arg)
                    if out is NotImplemented:
                        raise SettError
                return bool(out)

            def __entails__(self, other, /):
                return NotImplemented

            def union(self, other, /):
                return SettUnion(self, other)

            def __or__(self, other, /):
                return self.union(other)

            @property
            def __ror__(self, /):
                return self.__or__

            def intersection(self, other, /):
                return SettIntersection(self, other)

            def __and__(self, other, /):
                return self.intersection(other)

            @property
            def __rand__(self, /):
                return self.__and__

            def __xor__(self, other, /):
                return ~(self & other)

            @property
            def __rxor__(self, /):
                return self.__xor__

            def invert(self, /):
                return SettInverse(self)

            def __invert__(self, /):
                return self.invert()

            convert = staticmethod(convert)


class Degenerate(Sett, metaclass=_System):

    value: ...

    def get_signaltype(self, /):
        return type(self.value)

    def _contains_(self, arg, /):
        return arg is self.value

    def _includes_(self, arg, /):
        if isinstance(arg, Degenerate):
            return arg.member is self.value
        return super()._includes_()

    def __entails__(self, arg, /):
        return self.value in arg

    def __len__(self, /):
        return 1

    def __iter__(self, /):
        yield self.value


class Setts(Sett, metaclass=_Enumm):

    UNIVERSE: "The universal set, containing everything." = _Any_
    NULL: "The null set, containing nothing." = _Null_
    POWER: "The power set, containing all sets." = Sett

    def get_signaltype(self, /):
        return self._value_

    def _contains_(self, arg, /):
        return True

    def _includes_(self, arg, /):
        return True


class FuncSett(Sett, metaclass=_System):

    func: _collabc.Callable

    def get_signaltype(self, /):
        return next(iter(self.func.__annotations__.values(), Any))

    @property
    def _contains_(self, /):
        return self.func


class ContainerSett(Sett, metaclass=_System):

    container: _collabc.Container

    def get_signaltype(self, /):
        return tuple(sorted(set(map(type, self.container))))

    @property
    def _contains_(self, /):
        return self.container.__contains__

    def _includes_(self, arg, /):
        return all(map(self.container.__contains__, arg))


class TypeSett(Sett, metaclass=_Sprite):

    typ: type

    def get_signaltype(self, /):
        return self.typ

    def _contains_(self, arg, /):
        return isinstance(arg, self.typ)

    def _includes_(self, arg, /):
        return issubclass(arg, self.typ)


class SettBrace(Variadic, metaclass=_System):

    typ: KW[type] = tuple

    @property
    def breadth(self, /):
        return len(self.args)

    def get_signaltype(self, /):
        return self.typ

    def _contains_(self, other, /):
        if not isinstance(other, self.typ):
            return False
        return all(
            subarg in arg
            for arg, subarg in zip(self.args, other)
            )

    def _includes_(self, other, /):
        if not isinstance(other, self.__ptolemaic_class__):
            return False
        if other.breadth != self.breadth:
            return False
        if not issubclass(other.typ, self.typ):
            return False
        return all(
            asett.__includes__(bsett)
            for asett, bsett in zip(self.args, other.args)
            )


class SettInverse(Op, metaclass=_Sprite):

    sett: Sett

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.sett = cls.convert(params.sett)
        return bound

    def _contains_(self, arg, /):
        return arg not in self.sett

    def _includes_(self, arg, /):
        return not self.sett.__includes__(arg)

    def __inverse__(self, /):
        return self.sett


class SettUnion(Variadic):

    def get_signaltype(self, /):
        typs = tuple(sorted(set(sett.signaltype for sett in self.args)))
        if len(typs) == 1:
            return typs[0]
        return typs

    def _contains_(self, arg, /):
        for sett in self.args:
            if arg in sett:
                return True
        return False

    def _includes_(self, arg, /):
        for sett in self.args:
            if sett.__includes__(arg):
                return True
        return NotImplemented


class SettIntersection(Variadic):

    def get_signaltype(self, /):
        typs = tuple(sorted(set(sett.signaltype for sett in self.args)))
        if len(typs) == 1:
            return typs[0]
        return _pseudotype.TypeIntersection(*typs)

    def _contains_(self, arg, /):
        for sett in self.args:
            if arg not in sett:
                return False
        return True

    def _includes_(self, arg, /):
        return all(sett.__includes__(arg) for sett in self.args)


inverse = SettInverse.__class_call__
union = SettUnion.__class_call__
intersection = SettIntersection.__class_call__


_Stele_.complete()


###############################################################################
###############################################################################
