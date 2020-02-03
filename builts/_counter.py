import numpy as np

from ._producer import Producer
from ..value import Value

class Counter(Producer):
    def __init__(self, **kwargs):
        self.count = Value(0)
        self.counts = []
        self.counts_stored = []
        self.counts_disk = []
        outFn = lambda: None
        super().__init__(**kwargs)
        def out():
            yield np.array(self.count(), dtype = np.int32)
        self.outFns.append(out)
        self.outkeys.append('_count_')
        self.samples.append(np.array([0,], dtype = np.int32))
        def _post_store_fn():
            if self.count() in self.counts:
                discardedDatas = self.stored.pop()
                discardedCount = {
                    key: val \
                        for key, val in zip(self.outkeys, discardedDatas)
                    }['_count_']
                assert discardedCount == self.count()
            else:
                self.counts.append(self.count())
                self.counts_stored.append(self.count())
            self.stored.sort()
        def _post_save_fn():
            if len(self.stored) == 0:
                self.counts_disk.extend(self.counts_stored)
                self.counts_stored = []
                self.counts_disk = list(set(self.counts_disk))
        def _post_anchor_fn():
            self.counts_disk = list(set(self.reader[self.hashID, '_count_']))
            self.counts.extend(self.counts_disk)
            self.counts = list(set(self.counts))
        self._post_store_fns.append(_post_store_fn)
        self._post_save_fns.append(_post_save_fn)
        self._post_anchor_fns.append(_post_anchor_fn)