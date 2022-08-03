###############################################################################
''''''
###############################################################################


import itertools as _itertools
from collections import abc as _collabc

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.system import System as _System
from everest.ptolemaic.algebra import CompanionAlgebra as _CompanionAlgebra


class Brace(metaclass=_CompanionAlgebra):


    __mroclasses__ = dict(
        Power=('.Element.Unary', '.Base'),
        Finite='.Base',
        Single=('.Element.Unary', '.Finite'),
        Symmetric=('.Element.Unary', '.Finite'),
        Asymmetric=('.Element.Ennary', '.Finite'),
        )

    @classmethod
    def __class_call__(
            cls, arg0, /, *argn, labels=None, typ=NotImplemented
            ):
        if argn:
            args = (arg0, *argn)
            if labels is None:
                labels = tuple(_itertools.repeat(None, len(args)))
            if len(aset := set(args)) < 2:
                return cls.Symmetric(aset.pop(), labels=labels, typ=typ)
            return cls.Asymmetric(*args, labels=labels, typ=typ)
        if labels is Ellipsis:
            return cls.Power(arg0, typ=typ)
        if labels is None:
            labels = 1
        if isinstance(labels, int):
            if labels == 1:
                return cls.Single(arg0, typ=typ)
            else:
                labels = tuple(range(labels))
        return cls.Symmetric(arg0, labels=labels, typ=typ)

    @classmethod
    def _convert_(cls, arg, /):
        out = super()._convert_(arg)
        if out is not NotImplemented:
            return out
        if isinstance(arg, _collabc.Mapping):
            return cls(*arg.values(), labels=tuple(arg.keys()))
        if isinstance(arg, _collabc.Iterable):
            return cls(*arg)
        return cls(arg)

    @classmethod
    def merge(cls, /, *args):
        return cls(*_itertools.chain.from_iterable(
            cls.convert(arg).args for arg in args
            ))


    class Base(metaclass=_Essence):

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


    class Power(metaclass=_System):

        typ: KW[type] = tuple


    class Finite(metaclass=_System):

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


    class Single(metaclass=_System):

        @comp
        def args(self, /):
            return (self.arg,)

        def __neg__(self, /):
            return self.arg

        @property
        def breadth(self, /):
            return 1


    class Symmetric(metaclass=_System):

        labels: KW[...]

        @comp
        def args(self, /):
            arg = self.arg
            return tuple(arg for _ in range(len(self.labels)))


    class Asymmetric(metaclass=_System):

        labels: KW[...] = None



###############################################################################
###############################################################################
