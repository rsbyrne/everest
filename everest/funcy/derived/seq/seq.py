################################################################################

from functools import cached_property as _cached_property

from . import _reseed, _Derived, _special, _generic
from .seqiterable import SeqIterable as _SeqIterable

from .exceptions import *

class Seq(_Derived, _generic.FuncySequence):

    discrete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @_cached_property
    def seqIterable(self):
        return _SeqIterable(self)

    def evaluate(self):
        return self.seqIterable
    def purge(self):
        super().purge()
        self.seqIterable._get_index.cache_clear()
        self.seqIterable._get_slice.cache_clear()

    def _iter(self):
        return iter(self._value_resolve(self.prime))

    @_cached_property
    def seqTerms(self):
        return [t for t in self.fnTerms if isinstance(t, Seq)]
    def _seqLength(self):
        return _special.unkint
    def __len__(self):
        return self._seqLength()

    def arithmop(self, *args, **kwargs):
        return self.seqop(*args, **kwargs)

    @_cached_property
    def chained(self):
        return self.seqop.chainiter(self)
    @_cached_property
    def permuted(self):
        return self.seqop.productiter(self)
    @_cached_property
    def zipped(self):
        return self.seqop.zipiter(self)
    @_cached_property
    def muddled(self):
        return self.seqop.muddle(self)

class Seeded(Seq):
    @_cached_property
    def _startseed(self):
        return _reseed.digits(12, seed = self._value_resolve(self.terms[-1]))

################################################################################
