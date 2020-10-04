import numpy as np

from ._producer import Producer
from ._producer import AbortStore
from ..value import Value
from ..weaklist import WeakList
from ..anchor import NoActiveAnchorError

class Counter(Producer):

    _defaultCountsKey = 'count'

    def __init__(self, **kwargs):
        self.count = Value(-1)
        super().__init__(**kwargs)
        # Producer attributes:
        self._outFns.append(self._countoutFn)
        self._producer_outkeys.append(self._countsKeyFn)
        self._pre_store_fns.append(self._counter_pre_store_fn)
        self._post_store_fns.append(self._counter_sort_stored_fn)
        self._pre_save_fns.append(self._counter_pre_save_fn)
        # Built attributes:
#         self._post_anchor_fns.append(self._update_counts)

    def _countsKeyFn(self):
        return [self._defaultCountsKey,]
    @property
    def _countsKey(self):
        return self._countsKeyFn()[0]
    @property
    def _countsKeyIndex(self):
        return self.outkeys.index(self._countsKey)

    @property
    def counts_stored(self):
        storedCounts = sorted([
            row[self._countsKeyIndex] for row in self.stored
            ])
        assert sorted(set(storedCounts)) == storedCounts
        return storedCounts

    @property
    def counts_disk(self):
        try:
            counts = sorted(set(self.readouts[self._countsKey]))
            counts = [int(x) for x in counts]
            return counts
        except (KeyError, NoActiveAnchorError):
            return []

    @property
    def counts(self):
        return sorted(set([*self.counts_stored, *self.counts_disk]))

    def _counter_sort_stored_fn(self):
        self.stored.sort(key = lambda row: row[self._countsKeyIndex])

    def drop_count(self, count):
        del self.stored[self.counts_stored.index(count)]

    def _countoutFn(self):
        yield self.count.value

    def _counter_pre_store_fn(self):
        if self.count in self.counts_stored: raise AbortStore

    def _counter_pre_save_fn(self):
        keepCounts = [
            self.counts_stored.index(i)
                for i in self.counts_stored
                    if not i in self.counts_disk
            ]
        self.stored[:] = [self.stored[i] for i in keepCounts]
