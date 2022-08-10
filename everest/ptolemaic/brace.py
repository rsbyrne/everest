###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from .essence import Essence as _Essence
from .system import System as _System
from .algebra import (
    Algebra as _Algebra,
    AbstractAlgebra as _absalg,
    )
from .essence import Any as _Any, Null as _Null


class Brace(metaclass=_Algebra):


    def __class_getitem__(cls, arg, /):
        if isinstance(arg, tuple):
            return cls(*arg)
        return cls(arg)

    @classmethod
    def _parameterise_(
            cls, arg0, /, *argn, labels=None, typ=NotImplemented
            ):
        if argn:
            args = (arg0, *argn)
            if labels is None:
                labels = tuple(_itertools.repeat(None, len(args)))
            if len(aset := set(args)) < 2:
                cls.altreturn(cls.Symmetric(aset.pop(), labels=labels, typ=typ))
            cls.altreturn(cls.Asymmetric(*args, labels=labels, typ=typ))
        if labels is Ellipsis:
            cls.altreturn(cls.Power(arg0, typ=typ))
        if labels is None:
            labels = 1
        if isinstance(labels, int):
            if labels == 1:
                cls.altreturn(cls.Single(arg0, typ=typ))
            else:
                labels = tuple(range(labels))
        cls.altreturn(cls.Symmetric(arg0, labels=labels, typ=typ))

    @classmethod
    def _algconvert_(cls, arg, /):
        if isinstance(arg, _collabc.Mapping):
            return cls(*arg.values(), labels=tuple(arg.keys()))
        if isinstance(arg, _collabc.Iterable):
            return cls(*arg, labels=None)
        return cls.Single(arg)

    @classmethod
    def merge(cls, /, *args):
        return cls(*_itertools.chain.from_iterable(
            cls(arg).args for arg in args
            ), labels=None)


    class __Base__(mroclass):

        @property
        def typ(self, /):
            return tuple

        @property
        def args(self, /):
            raise TypeError("This kind of Brace cannot be unpacked.")

        @property
        def breadth(self, /):
            raise TypeError("This kind of Brace has undetermined breadth.")

        @property
        def labels(self, /):
            raise TypeError("This kind of Brace has no labels.")

        @property
        def shape(self, /):
            return (self.breadth,)


    class Power(
            mroclass('.__Unary__',),
            metaclass=_System,
            ):

        arg: pathget('..Base', fallback=_Null)
        typ: KW[type] = tuple


    class __Finite__(
            mroclass('.__Base__'),
            metaclass=_System,
            ):

        typ: KW[type] = tuple

        @comp
        def breadth(self, /):
            return len(self.labels)

        def __neg__(self, /):
            return self.args

        def __mul__(self, other, /):
            return self.algebra.merge(self, other)

        def __rmul__(self, other, /):
            return self.algebra.merge(other, self)


    class Single(
            mroclass('.__Unary__', '.__Finite__'),
            metaclass=_System,
            ):

        arg: pathget('..Base', fallback=_Null)

        @comp
        def args(self, /):
            return (self.arg,)

        def __neg__(self, /):
            return self.arg

        @property
        def breadth(self, /):
            return 1


    class Symmetric(
            mroclass('.__Unary__', '.__Finite__'),
            metaclass=_System,
            ):

        arg: pathget('..Base', fallback=_Null)
        labels: KW

        @comp
        def args(self, /):
            arg = self.arg
            return tuple(arg for _ in range(len(self.labels)))


    class Asymmetric(
            mroclass('.__Ennary__', '.__Finite__'),
            metaclass=_System,
            ):

        args: pathget('..Base', fallback=_Null)
        labels: KW = None


###############################################################################
###############################################################################
