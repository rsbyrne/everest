###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import inspect as _inspect
import types as _types
import sys as _sys
import itertools as _itertools

from . import ptolemaic as _ptolemaic
from .essence import Essence as _Essence
from .enumm import Enumm as _Enumm
from .system import System as _System
from . import pseudotype as _pseudotype
from .algebra import Algebra as _Algebra
from .brace import Brace as _Brace


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


class Sett(metaclass=_Algebra):


    __mroclasses__ = dict(
        FromFunc='.Base',
        FromContainer='.Base',
        FromType='.Base',
        Degenerate=('.Nullary', '.Base'),
        Inverse=('.Unary', '.Base'),
        Union=('.Ennary', '.Base'),
        Intersection=('.Ennary', '.Base'),
        Brace='.Base',
        )

    @classmethod
    def _convert_(cls, arg, /):
        out = super()._convert_(arg)
        if out is not NotImplemented:
            return out
        if arg is cls.Base:
            return cls.Identity.POWER
        if isinstance(arg, type):
            # if isinstance(arg, _types.GenericAlias):
            #     return cls.Brace(*map(arg.__args__), typ=arg.__orign__)
            return cls.FromType(arg)
        if arg is NotImplemented:
            return cls.NULL
        if arg in (_inspect._empty, Ellipsis):
            return cls.UNIVERSE
        if isinstance(arg, _collabc.Container):
            return cls.FromContainer(arg)
        if isinstance(arg, _types.FunctionType):
            return cls.FromFunc(arg)
        return NotImplemented

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.Base.bracetyp = cls.Brace


    class Base(metaclass=_Essence):

        __req_slots__ = dict(_signaltype=None)

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
                elif isinstance(typ, self.algebra):
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
            algtyp = self.algebra
            if arg is algtyp.NULL:
                return True
            if not isinstance(arg, algtyp):
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
            return self.algebra.Union(self, other)

        def __or__(self, other, /):
            return self.union(other)

        @property
        def __ror__(self, /):
            return self.__or__

        def intersection(self, other, /):
            return (
                self.algebra.Intersection
                (self, other)
                )

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
            return self.algebra.Inverse(self)

        def __invert__(self, /):
            return self.invert()

        # def __pos__(self, /):
        #     return self.bracetyp(self)

        def __pow__(self, other, /):
            return self.bracetyp(self, labels=other)

        def __mul__(self, other, /):
            return self.bracetyp.merge(self, other)

        def __rmul__(self, other, /):
            return self.bracetyp.merge(other, self)


    class Identity(metaclass=_Enumm):

        UNIVERSE: "The universal set, containing everything." = _Any_
        NULL: "The null set, containing nothing." = _Null_
        POWER: "The power set, containing all sets." = None

        def get_signaltype(self, /):
            return self._value_

        def _contains_(self, arg, /):
            return True

        def _includes_(self, arg, /):
            return True


    class FromFunc(metaclass=_System):

        func: _collabc.Callable

        def get_signaltype(self, /):
            return next(iter(self.func.__annotations__.values(), Any))

        @property
        def _contains_(self, /):
            return self.func


    class FromContainer(metaclass=_System):

        container: _collabc.Container

        def get_signaltype(self, /):
            return tuple(sorted(set(map(type, self.container))))

        @property
        def _contains_(self, /):
            return self.container.__contains__

        def _includes_(self, arg, /):
            return all(map(self.container.__contains__, arg))


    class FromType(metaclass=_System):

        typ: type

        def get_signaltype(self, /):
            return self.typ

        def _contains_(self, arg, /):
            return isinstance(arg, self.typ)

        def _includes_(self, arg, /):
            return issubclass(arg, self.typ)


    class Inverse(metaclass=_System):

        __algparams__ = dict(
            invertible=True,
            )

        def _contains_(self, arg, /):
            return arg not in self.arg

        def _includes_(self, arg, /):
            return not self.arg.__includes__(arg)


    class Union(metaclass=_System):

        __algparams__ = dict(
            unique=True, associative=True, commutative=True
            )

        def get_signaltype(self, /):
            typs = _ptolemaic.PtolUniTuple(
                sett.signaltype for sett in self.args
                )
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


    class Intersection(metaclass=_System):

        __algparams__ = dict(
            unique=True, associative=True, commutative=True
            )

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


    class Degenerate(metaclass=_System):

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


    class Brace(_Brace):


        __mroclasses__ = dict(Base='..Base')


        class Base(metaclass=_Essence):

            def get_signaltype(self, /):
                return self.typ

            def _contains_(self, other, /):
                if not isinstance(other, self.typ):
                    return False
                return all(
                    subarg in arg
                    for arg, subarg in _itertools.zip_longest(self.args, other)
                    )

            def _includes_(self, other, /):
                basecls = self.AlgebraicType
                if not isinstance(other, basecls):
                    return False
                if other.breadth != self.breadth:
                    return False
                if not issubclass(other.typ, self.typ):
                    return False
                return all(
                    asett.__includes__(bsett)
                    for asett, bsett in zip(self.args, other.args)
                    )

        class Power(metaclass=_System):

            def _contains_(self, other, /):
                if not isinstance(other, self.typ):
                    return False
                arg = self.arg
                for item in other:
                    if item not in arg:
                        return False
                return True


_sys.modules[__name__] = Sett


###############################################################################
###############################################################################
