################################################################################

from .exceptions import *

from functools import cached_property
from collections.abc import Iterable
from itertools import product

from everest import reseed

from ..base import Function
from ..derived import Derived
from ..special import *
from .seqiterable import SeqIterable
from .sequtils import seqlength

class Seq(Derived, Iterable):

    discrete = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @cached_property
    def seqIterable(self):
        return SeqIterable(self)

    def evaluate(self):
        return self.seqIterable
    def purge(self):
        super().purge()
        self.seqIterable._get_index.cache_clear()
        self.seqIterable._get_slice.cache_clear()

    def _iter(self):
        return iter(self._value_resolve(self.prime))

#     def __iter__(self):
#         return iter(self.value)

    @cached_property
    def seqTerms(self):
        return [t for t in self.fnTerms if isinstance(t, Seq)]
    def _seqLength(self):
        return unkint
    def __len__(self):
        return self._seqLength()

    def op(self, *args, **kwargs):
        return self.seqop(*args, **kwargs)
    def seqop(self, *args, op, rev = False, **kwargs):
        if rev:
            return self.Fn.seq.op(
                op, *(*args, self),
                **kwargs
                )
        else:
            return self.Fn.seq.op(
                op, self, *args,
                **kwargs
                )
    def arithmop(self, *args, **kwargs):
        return self.seqop(*args, **kwargs)

    @cached_property
    def chained(self):
        return self.seqop.chainiter(self)
    @cached_property
    def permuted(self):
        return self.seqop.productiter(self)
    @cached_property
    def zipped(self):
        return self.seqop.zipiter(self)
    @cached_property
    def muddled(self):
        return self.seqop.muddle(self)

class Seeded(Seq):
    @cached_property
    def _startseed(self):
        return reseed.digits(12, seed = self._value_resolve(self.terms[-1]))

    # def __len__(self):
    #     return len(self.value[0])
    # def __getitem__(self, arg):
    #     if type(arg) is slice:
    #         return self._getslice(arg)
    #     else:
    #         return self.op(arg, op = 'getitem')
    # def _getslice(self, slicer):
    #     start, stop, step = slicer.start, slicer.stop, slicer.step
    #     start = 0 if start is None else start
    #     stop = len(self) if stop is None else min(len(self, stop))
    #     step = 1 if step is None else step
    #     return (self[i] for i in range(start, stop, step))
    # def __iter__(self):
    #     return (self[i] for i in range(len(self)))

################################################################################
