import numpy as np

from ._producer import Producer
from ..value import Value

class Counter(Producer):
    def __init__(self, **kwargs):
        self.count = Value(0)
        self.counts = []
        self.counts_stored = []
        self.counts_disk = []
        self.indexKey = 'count'
        super().__init__(**kwargs)
        # Producer attributes:
        self._outFns.append(self.countoutFn)
        self.outkeys.append('count')
        self.samples.append(np.array([0,], dtype = np.int32))
        self._post_store_fns.append(self._counter_post_store_fn)
        self._post_save_fns.append(self._counter_post_save_fn)
        # Built attributes:
        self._post_anchor_fns.append(self._counter_post_anchor_fn)

    def countoutFn(self):
        yield np.array(self.count(), dtype = np.int32)

    def _counter_post_store_fn(self):
        if self.count() in self.counts:
            discardedDatas = self.stored.pop()
            discardedCount = {
                key: val \
                    for key, val in zip(self.outkeys, discardedDatas)
                }['count']
            assert discardedCount == self.count()
        else:
            self.counts.append(self.count())
            self.counts_stored.append(self.count())
        self.stored.sort()
    def _counter_post_save_fn(self):
        if len(self.stored) == 0:
            self.counts_disk.extend(self.counts_stored)
            self.counts_stored = []
            self.counts_disk = list(set(self.counts_disk))
    def _counter_post_anchor_fn(self):
        try: self.counts_disk = list(set(self.reader[
            self.hashID, 'outputs', 'count'
            ]))
        except KeyError: pass
        self.counts.extend(self.counts_disk)
        self.counts = list(set(self.counts))
