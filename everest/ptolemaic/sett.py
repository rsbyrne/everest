###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import inspect as _inspect
import types as _types
import sys as _sys

from . import ptolemaic as _ptolemaic
from .essence import Essence as _Essence
from .enumm import Enumm as _Enumm
from .sprite import Sprite as _Sprite
from .system import System as _System
from .stele import Stele as _Stele
from . import pseudotype as _pseudotype


class _SteleType_(metaclass=_Stele):

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


_SteleType_.commence()


def convert(arg, /):
    if isinstance(arg, Sett):
        return arg
    if arg is Sett:
        return POWER
    if arg in (None, _inspect._empty):
        return UNIVERSE
    if isinstance(arg, _collabc.Container):
        return ContainerSett(arg)
    if isinstance(arg, type):
        if isinstance(arg, _types.GenericAlias):
            return BraceSett(
                tuple(map(convert, arg.__args__)), arg.__origin__
                )
        return TypeSett(arg)
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


class _Null_(metaclass=_Essence):

    @classmethod
    def __class_instancecheck__(cls, other, /):
        return False

    @classmethod
    def __subclasshook__(cls, other, /):
        if cls is _Null_:
            return False
        return NotImplemented


class Sett(metaclass=_Essence):

    __req_slots__ = dict(signaltype=None)

    def __init__(self, /):
        typ = self.get_signaltype()
        if typ is None:
            typ = _Null_
        elif typ is Ellipsis:
            typ = _Any_
        self.signaltype = typ

    def get_signaltype(self, /):
        return _Any_

    def __sett_contains__(self, arg, /):
        return NotImplemented

    def __contains__(self, arg, /):
        out = self.__sett_contains__(arg)
        if out is NotImplemented:
            try:
                meth = arg.__constitutes__
            except AttributeError:
                raise NotImplementedError
            out = meth(arg)
        return bool(out)

    def __sett_includes__(self, arg, /):
        return NotImplemented

    def __includes__(self, arg, /):
        out = self.__sett_includes__(arg)
        if out is NotImplemented:
            try:
                meth = arg.__comprises__
            except AttributeError:
                raise NotImplementedError
            out = meth(arg)
        return bool(out)

    def __or__(self, other, /):
        if isinstance(other, SettUnion):
            return SettUnion(self, *other)
        return SettUnion(self, other)

    @property
    def __ror__(self, /):
        return self.__or__

    def __and__(self, other, /):
        if isinstance(other, SettIntersection):
            return SettIntersection(self, *other)
        return SettIntersection(self, other)

    @property
    def __rand__(self, /):
        return self.__and__

    def __xor__(self, other, /):
        return ~SettIntersection(self, other)

    @property
    def __rxor__(self, /):
        return self.__xor__

    def __invert__(self, /):
        return SettInverse(self)


class Setts(Sett, metaclass=_Enumm):

    UNIVERSE: None = _Any_
    NULL: None = _Null_
    POWER: None = Sett

    def __sett_contains__(self, arg, /):
        return isinstance(arg, self._value_)


class FuncSett(Sett, metaclass=_System):

    func: _collabc.Callable

    def get_signaltype(self, /):
        return next(iter(self.func.__annotations__.values(), Any))

    @property
    def __sett_contains__(self, /):
        return self.func


class ContainerSett(Sett, metaclass=_System):

    container: _collabc.Container

    def get_signaltype(self, /):
        return tuple(sorted(set(map(type, self.container))))

    @property
    def __sett_contains__(self, /):
        return self.container.__contains__

    def __sett_includes__(self, arg, /):
        return all(map(self.container.__contains__, arg))


class TypeSett(Sett, metaclass=_Sprite):

    typ: type

    def get_signaltype(self, /):
        return self.typ

    def __sett_contains__(self, arg, /):
        return isinstance(arg, self.typ)

    def __sett_includes__(self, arg, /):
        return issubclass(arg, self.typ)


class BraceSett(Sett, metaclass=_Sprite):

    setts: _collabc.Iterable
    typ: type = tuple

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.setts = tuple(map(convert, params.setts))
        return params

    @property
    def breadth(self, /):
        return len(self.setts)

    def get_signaltype(self, /):
        return self.typ

    def __sett_contains__(self, arg, /):
        if not isinstance(arg, self.typ):
            return False
        return all(
            subarg in sett
            for sett, subarg in zip(self.setts, arg)
            )

    def __sett_includes__(self, arg, /):
        if not isinstance(arg, BraceSett):
            return False
        if arg.breadth != self.breadth:
            return False
        if not issubclass(arg.typ, self.typ):
            return False
        return all(
            asett.__includes__(bsett)
            for asett, bsett in zip(self.setts, arg.setts)
            )


class Op(Sett):
    ...


class Inverse(Op, metaclass=_Sprite):

    sett: Sett

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.sett = convert(params.sett)
        return bound

    def __sett_contains__(self, arg, /):
        return arg not in self.sett

    def __sett_includes__(self, arg, /):
        return not self.sett.__includes__(arg)

    def __inverse__(self, /):
        return self.sett


class MultiOp(Op, metaclass=_Sprite):

    setts: Sett

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        out = super().__class_call__(*args, **kwargs)
        if (nsetts := len(setts := out.setts)) == 0:
            return Setts.NULL
        elif nsetts == 1:
            return setts[0]
        return out

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        params.setts = tuple(sorted(set(map(convert, params.setts))))
        return params


class Union(MultiOp):

    def get_signaltype(self, /):
        typs = tuple(sorted(set(sett.signaltype for sett in self.setts)))
        if len(typs) == 1:
            return typs[0]
        return typs

    def __sett_contains__(self, arg, /):
        for sett in self.setts:
            if arg in sett:
                return True
        return False

    def __sett_includes__(self, arg, /):
        for sett in self.setts:
            if sett.__includes__(arg):
                return True
        return NotImplemented


class Intersection(MultiOp):

    def get_signaltype(self, /):
        typs = tuple(sorted(set(sett.signaltype for sett in self.setts)))
        if len(typs) == 1:
            return typs[0]
        return _pseudotype.TypeIntersection(*typs)

    def __sett_contains__(self, arg, /):
        for sett in self.setts:
            if arg not in sett:
                return False
        return True

    def __sett_includes__(self, arg, /):
        return all(sett.__includes__(arg) for sett in self.setts)


inverse = Inverse.__class_call__
union = Union.__class_call__
intersection = Intersection.__class_call__


_SteleType_.complete()


###############################################################################
###############################################################################
