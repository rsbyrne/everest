###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import inspect as _inspect
import types as _types
# import sys as _sys
import itertools as _itertools

from . import ptolemaic as _ptolemaic
from .essence import Essence as _Essence
from .enumm import Enumm as _Enumm
from .system import System as _System
from . import pseudotype as _pseudotype
from .algebra import Algebra as _Algebra
from .brace import Brace as _Brace


class Sett(metaclass=_Algebra):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.Base.bracetyp = cls.Brace
        cls.Base.register(cls._NullSett_)

    @classmethod
    def _algconvert_(cls, arg, /):
        if arg is cls.Base:
            return cls.Special.POWER
        if isinstance(arg, type):
            if isinstance(arg, _types.GenericAlias):
                args, origin = arg.__args__, arg.__origin__
                if len(args) == 1:
                    labels = ...
                else:
                    labels = None
                return cls.Brace(*map(cls, args), labels=labels, typ=origin)
            return cls.FromType(arg)
        if arg is None:
            return cls.NULL
        if arg in (_inspect._empty, Ellipsis):
            return cls.UNIVERSE
        if isinstance(arg, _collabc.Container):
            return cls.FromContainer(arg)
        if isinstance(arg, _types.FunctionType):
            return cls.FromFunc(arg)
        return NotImplemented


    Element = _Any_


    class Base(mroclass('..Operation')):

        __req_slots__ = dict(_signaltype=None)

        @property
        def signaltype(self, /):
            try:
                return object.__getattribute__(self, '_signaltype')
            except AttributeError:
                typ = self.get_signaltype()
                if typ is None:
                    typ = _Null_
                elif typ is Ellipsis:
                    typ = _Any_
                elif isinstance(typ, self.algebra):
                    typ = typ.signaltype
                object.__setattr__(self, '_signaltype', typ)
                return typ

        def get_signaltype(self, /):
            return self.algebra.Element

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

        def __pow__(self, other, /):
            return self.bracetyp(self, labels=other)

        def __mul__(self, other, /):
            return self.bracetyp.merge(self, other)

        def __rmul__(self, other, /):
            return self.bracetyp.merge(other, self)

        # def __pos__(self, /):
        #     return self.bracetyp(self)


    class _NullSett_(Base, metaclass=_System):

        def __contains__(self, arg, /):
            return False

        def __includes__(self, arg, /):
            return arg is self

        def __entails__(self, arg, /):
            return True


    NULL = _NullSett_()


    class Special(mroclass):

        @member
        @property
        def UNIVERSE(self, /):
            "The universal set, containing everything."
            return (alg := self.algebra)(alg.Element)

        @member
        @property
        def POWER(self, /):
            "The power set, containing all sets."
            return Sett(self.algebra)

        def get_signaltype(self, /):
            return self.value.signaltype

        def _contains_(self, arg, /):
            return self.value._contains_(arg)

        def _includes_(self, arg, /):
            return self.value._includes_(arg)


    class FromFunc(mroclass('.Base'), metaclass=_System):

        func: _collabc.Callable

        def get_signaltype(self, /):
            return next(iter(self.func.__annotations__.values(), Any))

        @property
        def _contains_(self, /):
            return self.func


    class FromContainer(mroclass('.Base'), metaclass=_System):

        container: _collabc.Container

        def get_signaltype(self, /):
            return tuple(sorted(set(map(type, self.container))))

        @property
        def _contains_(self, /):
            return self.container.__contains__

        def _includes_(self, arg, /):
            return all(map(self.container.__contains__, arg))


    class FromType(mroclass('.Base'), metaclass=_System):

        typ: type

        @classmethod
        def _parameterise_(cls, /, *args, **kwargs):
            params = super()._parameterise_(*args, **kwargs)
            if not issubclass(typ := params.typ, cls.algebra.Element):
                raise ValueError(typ)
            return params

        def get_signaltype(self, /):
            return self.typ

        def _contains_(self, arg, /):
            return isinstance(arg, self.typ)

        def _includes_(self, arg, /):
            return issubclass(arg, self.typ)


    class Degenerate(mroclass('.Nullary', '.Base'), metaclass=_System):

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


    class Inverse(mroclass('.Unary', '.Base'), metaclass=_System):

        __algparams__ = dict(
            invertible=True,
            )

        def _contains_(self, arg, /):
            return arg not in self.arg

        def _includes_(self, arg, /):
            return not self.arg.__includes__(arg)


    class Union(mroclass('.Ennary', '.Base'), metaclass=_System):

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


    class Intersection(mroclass('.Ennary', '.Base'), metaclass=_System):

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


    class Brace(mroclass(_Brace)):


        class Base(mroclass('..Base')):

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

        class Power(mroclass, metaclass=_System):

            def _contains_(self, other, /):
                if not isinstance(other, self.typ):
                    return False
                arg = self.arg
                for item in other:
                    if item not in arg:
                        return False
                return True


# _sys.modules[__name__] = Sett


###############################################################################


# assert ('foo', 1., 2) in \
#     Sett(str) * Sett(float) * Sett(int)

# assert ('foo', (1., 2)) in \
#     Sett(str) * (Sett(float) * Sett(int))**1

# assert ((0, 1), (2, 3), (4, 5)) in \
#     (Sett(int)**2)**3

# assert ((), (1, 2), (3, 4, 5)) in \
#     (Sett(int)**...)**3


###############################################################################
