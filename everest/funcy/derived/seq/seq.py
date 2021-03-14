################################################################################

from functools import cached_property as _cached_property
from abc import abstractmethod as _abstractmethod

from . import _reseed, _Derived, _special, _generic

from .exceptions import *

class Seq(_Derived, _generic.FuncyBroadIncisor):

    discrete = False
    isSeq = True

    def _evaluate(*_, **__):
        return NotImplemented
    @_abstractmethod
    def _iter(self):
        raise _generic.FuncyAbstractMethodException

    def _seqLength(self):
        return _special.unkint

class _SeqIncised(_Derived):
    _incisionType = _generic.FuncyIncisor
    def __init__(self, seq, incisor, /, **kwargs):
        super().__init__(seq, incisor, **kwargs)
        self.seq, self.incisor = self.terms
        if isinstance(self.seq, self._Fn.Function):
            if not self.seq.isSeq:
                raise TypeError("Seq input must be .isSeq!")
        else:
            raise TypeError(
                "Seq input must be a Function or convertable to one,"
                f" not {type(self.seq)}"
                )
        if not isinstance(self.incisor, self._incisionType):
            raise TypeError(
                "Incisor input must be a subclass of FuncyBroadIncisor,"
                f" not {type(self.incisor)}"
                )

class SeqSwathe(_SeqIncised, Seq):
    _incisionType = _generic.FuncyBroadIncisor
    def __init__(self, seq, incisor, /, **kwargs):
        if not isinstance(incisor, self._Fn.Function):
            incisor = self._Fn[incisor]
        super().__init__(seq, incisor, **kwargs)
    def _seqLength(self):
        return min()
    def _iter(self):
        indices, values = iter(self.incisor.value), iter(self.seq.value)
        ti = next(indices)
        for i, v in enumerate(values):
            if i == ti:
                yield v
                try:
                    ti = next(indices)
                except StopIteration:
                    break

class SeqElement(_SeqIncised):
    _incisionType = _generic.FuncyStrictIncisor
    @property
    def isSeq(self):
        return False
    def _evaluate(self, terms):
        seqiter, incisor = terms
        return seqiter[incisor]

class Seeded(Seq):
    @_cached_property
    def _startseed(self):
        return _reseed.digits(12, seed = self._value_resolve(self.terms[-1]))

################################################################################
