###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import inspect as _inspect
import types as _types
import sys as _sys

from everest.ur import Dat as _Dat

from .essence import Essence as _Essence
from .enumm import Enumm as _Enumm
from .sprite import ModuleMate as _ModuleMate
from .armature import Armature as _Armature, Field as _Field
from .utilities import (
    TypeIntersection as _TypeIntersection,
    TypeBrace as _TypeBrace,
    )


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
        return TypeSett(arg)
    if isinstance(arg, _types.FunctionType):
        return FuncSett(arg)
    raise TypeError(arg, type(arg))


class Sett(metaclass=_Essence):

    __req_slots__ = ('signaltype',)

    def __init__(self, /):
        self.signaltype = self.get_signaltype()

    def get_signaltype(self, /):
        return object

    @_abc.abstractmethod
    def __contains__(self, arg, /):
        raise NotImplementedError

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

    __enumerators__ = dict(
        UNIVERSE=_Dat.__instancecheck__,
        NULL=(lambda x: False),
        POWER=Sett.__instancecheck__,
        )

    def __contains__(self, arg, /):
        return self.val(arg)


globals().update({enum.name: enum for enum in Setts})


class FuncSett(Sett, metaclass=_Armature):

    func: _Armature.Field.POS[_collabc.Callable]

    def get_signaltype(self, /):
        return next(iter(self.func.__annotations__.values(), object))

    @property
    def __contains__(self, /):
        return self.func


class ContainerSett(Sett, metaclass=_Armature):

    container: _Armature.Field.POS[_collabc.Container]

    def get_signaltype(self, /):
        return tuple(sorted(set(map(type, self.container))))

    @property
    def __contains__(self, /):
        return self.container.__contains__


class TypeSett(Sett, metaclass=_Armature):

    typ: _Armature.Field.POS[type]

    def get_signaltype(self, /):
        return self.typ

    def __contains__(self, arg, /):
        return isinstance(arg, self.typ)


class Brace(Sett, metaclass=_Armature):

    setts: _Armature.Field.POS[_collabc.Iterable]

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.setts = tuple(map(convert, params.setts))
        return params

    def get_signaltype(self, /):
        return _TypeBrace(*(sett.signaltype for sett in self.setts))

    def __contains__(self, arg, /):
        return all(
            subarg in sett
            for sett, subarg in zip(self.setts, arg)
            )


class Op(Sett):
    ...


class Inverse(Op, metaclass=_Armature):

    sett: _Armature.Field.POS[Sett]

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.sett = convert(params.sett)
        return bound

    def __contains__(self, arg, /):
        return arg not in self.sett

    def __inverse__(self, /):
        return self.sett


class MultiOp(Op, metaclass=_Armature):
    
    setts: _Armature.Field.ARGS[Sett]

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        out = super().__class_call__(*args, **kwargs)
        if (nsetts := len(setts := out.setts)) == 0:
            return Setts.NULL
        elif nsetts == 1:
            return setts[0]
        return out

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.setts = tuple(sorted(set(map(convert, params.setts))))
        return params


class Union(MultiOp):

    def get_signaltype(self, /):
        return tuple(sett.signaltype for sett in self.setts)

    def __contains__(self, arg, /):
        for sett in self.setts:
            if arg in sett:
                return True
        return False


class Intersection(MultiOp):

    def get_signaltype(self, /):
        return _TypeIntersection(*(sett.signaltype for sett in self.setts))

    def __contains__(self, arg, /):
        for sett in self.setts:
            if arg not in sett:
                return False
        return True


inverse = Inverse.__class_call__
union = Union.__class_call__
intersection = Intersection.__class_call__


class _SettModuleMate_(_ModuleMate):

    def __call__(self, arg, /):
        if arg is self:
            arg = Sett
        return convert(arg)

    def __instancecheck__(self, arg, /):
        return isinstance(arg, Sett)

    def __subclasscheck__(self, arg, /):
        return issubclass(arg, Sett)


_SettModuleMate_(__name__)


###############################################################################
###############################################################################
