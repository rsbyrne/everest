import numpy as np

from ._producer import Producer
from ._producer import AbortStore
from ..value import Value
from ..weaklist import WeakList

class Counter(Producer):

    _countsKey = 'count'

    def __init__(self, **kwargs):
        self._count_update_fns = WeakList()
        self.count = Value(-1)
        super().__init__(**kwargs)
        # Producer attributes:
        self._outFns.append(self.countoutFn)
        self.outkeys.append(self._countsKey)
        self._pre_store_fns.append(self._counter_pre_store_fn)
        self._pre_save_fns.append(self._counter_pre_save_fn)
        self._post_reroute_outputs_fns.append(self._counter_post_reroute_fn)
        # Built attributes:
#         self._post_anchor_fns.append(self._update_counts)

    def _counter_post_reroute_fn(self):
        self.count.value = -1

    @property
    def counts_stored(self):
        countsIndex = self.outkeys.index(self._countsKey)
        storedCounts = [row[countsIndex] for row in self.stored]
        assert sorted(set(storedCounts)) == storedCounts
        return storedCounts

    @property
    def counts_disk(self):
        if not self.anchored:
            return []
        try:
            counts = list(set(self.readouts[self._countsKey]))
            counts = [int(x) for x in counts]
            return counts
        except KeyError:
            return []

    @property
    def counts(self):
        return sorted(set([*self.counts_stored, *self.counts_disk]))

    def _count_update_fn(self):
        for fn in self._count_update_fns: fn()

    def countoutFn(self):
        self._count_update_fn()
        yield self.count.value

    def _counter_pre_store_fn(self):
        if self.count in self.counts_stored: raise AbortStore

    def _counter_pre_save_fn(self):
        clashCounts = [i for i in self.counts_stored if i in self.counts_disk]
        junkStoreds = [self.stored.pop[i] for i in clashCounts] # left for garbage coll.
