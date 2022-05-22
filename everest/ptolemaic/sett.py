###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import abc as _collabc
import types as _types

from everest.ur import Dat as _Dat

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ousia import Funcc as _Funcc
from everest.ptolemaic.compound import Compound as _Compound
from everest.ptolemaic.field import Field as _Field


def convert(arg, /):
    if arg is None:
        return UNIVERSE
    if isinstance(arg, Sett):
        return arg
    if isinstance(arg, _collabc.Container):
        return ContainerSett(arg)
    if isinstance(arg, type):
        return TypeSett(arg)
    if isinstance(arg, _types.FunctionType):
        return FuncSett(arg)
    raise TypeError(arg, type(arg))


class Sett(metaclass=_Essence):

    def __contains_like__(self, arg: type, /):
        return issubclass(arg, object)

    @_abc.abstractmethod
    def __contains__(self, arg, /):
        raise NotImplementedError

    @classmethod
    def __class_call__(cls, arg, /):
        if cls is Sett:
            return convert(arg)
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


class FuncSett(_Funcc, Sett):

    @property
    def __contains__(self, /):
        return self.func


class ContainerSett(_Compound.BaseTyp, Sett):

    container: _Field.POS[_collabc.Container]

    @property
    def __contains__(self, /):
        return self.container.__contains__


class TypeSett(_Compound.BaseTyp, Sett):

    typ: _Field.POS[type]

    def __contains_like__(self, arg: type, /):
        return issubclass(arg, self.typ)

    def __contains__(self, arg, /):
        return isinstance(arg, self.typ)


class SettOp(Sett):
    ...


class SettInverse(_Compound.BaseTyp, SettOp):

    sett: _Field.POS[Sett]

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.sett = convert(params.sett)
        return bound

    def __contains__(self, arg, /):
        return arg not in self.sett

    def __inverse__(self, /):
        return self.sett


class SettMultiOp(_Compound.BaseTyp, SettOp):
    
    setts: _Field.ARGS

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        out = super().__class_call__(*args, **kwargs)
        if (nsetts := len(setts := out.setts)) == 0:
            return EMPTY
        elif nsetts == 1:
            return setts[0]
        return out

    @classmethod
    def parameterise(cls, /, *setts):
        return super().parameterise(*(sorted(set(map(convert, setts)))))


class SettUnion(SettMultiOp):

    def __contains_like__(self, arg: type, /):
        for sett in self.setts:
            if sett.__contains_like__(arg):
                return True
        return False

    def __contains__(self, arg, /):
        for sett in self.setts:
            if arg in sett:
                return True
        return False


class SettIntersection(SettMultiOp):

    def __contains_like__(self, arg: type, /):
        for sett in self.setts:
            if not sett.__contains_like__(arg):
                return False
        return True

    def __contains__(self, arg, /):
        for sett in self.setts:
            if arg not in sett:
                return False
        return True


@Sett
def UNIVERSE(arg, /):
    return isinstance(arg, _Dat)

@Sett
def NULL(arg, /):
    return False


###############################################################################
###############################################################################
