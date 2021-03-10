################################################################################

from functools import cached_property as _cached_property
from abc import abstractmethod as _abstractmethod

from . import _reseed, _Derived, _special, _generic

from .exceptions import *

class Seq(_Derived):

    discrete = False
    isSeq = True

    def _evaluate(*_, **__):
        return NotImplemented
    @_abstractmethod
    def _iter(self):
        raise _generic.FuncyAbstractMethodException

    def _seqLength(self):
        return _special.unkint

class Seeded(Seq):
    @_cached_property
    def _startseed(self):
        return _reseed.digits(12, seed = self._value_resolve(self.terms[-1]))

################################################################################
