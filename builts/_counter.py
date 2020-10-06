import numpy as np
from functools import wraps

from ._indexer import Indexer, _indexer_load_wrapper, IndexerNullVal
from ._producer import AbortStore, LoadFail
from ..value import Value
from ..anchor import NoActiveAnchorError

from .. import exceptions
class CounterException(exceptions.EverestException):
    pass
class CountAlreadyLoadedError(CounterException):
    pass
class CounterLoadFail(CounterException, LoadFail):
    pass

class Counter(Indexer):

    _defaultCountsKey = 'count'
    _defaultCountNullVal = -999999999

    def __init__(self, **kwargs):
        self._countNullVal = self._defaultCountNullVal
        self.count = Value(self._countNullVal)
        self.countsKey = self._defaultCountsKey
        super().__init__(**kwargs)

    def _indexers(self):
        for o in super()._indexers(): yield o
        yield self.count
    def _indexerKeys(self):
        for o in super()._indexerKeys(): yield o
        yield self.countsKey
    def _indexerTypes(self):
        for o in super()._indexerTypes(): yield o
        yield np.int
    def _indexerNulls(self):
        for o in super()._indexerNulls(): yield o
        yield self._countNullVal

    def _outkeys(self):
        for o in super()._outkeys(): yield o
        yield self.countsKey
    def _out(self):
        for o in super()._out(): yield o
        yield self.count.value

    @property
    def _countsKeyIndex(self):
        return self.outkeys.index(self.countsKey)
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
            counts = self.readouts[self.countsKey]
            assert len(set(counts)) == len(counts)
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
    def _store(self):
        if self.count in self.counts_stored:
            raise AbortStore
        super()._store()

    def _save(self):
        keepCounts = [
            self.counts_stored.index(i)
                for i in self.counts_stored
                    if not i in self.counts_disk
            ]
        self.stored[:] = [self.stored[i] for i in keepCounts]
        super()._save()

    @_indexer_load_wrapper
    def load_count_stored(self, count):
        return self.load_index_stored(self.counts_stored.index(count))
    @_indexer_load_wrapper
    def load_count_disk(self, count):
        return self.load_index_disk(self.counts_disk.index(count))
    def load_count(self, count):
        try:
            return self.load_count_stored(count)
        except ValueError:
            return self.load_count_disk(count)
    def _load_process(self, outs):
        self.count.value = outs.pop(self.countsKey)
        return super()._load_process(outs)
    def _load(self, arg):
        i, ik, it, i0 = self._get_indexInfo(arg)
        if i is self.count:
            try:
                self.load_count(arg)
            except ValueError:
                raise CounterLoadFail
        else:
            super()._load(arg)

    def _nullify_count(self):
        self.count.value = self._countNullVal
    @property
    def _count_isNull(self):
        try:
            self._process_index(self.count.value)
            return False
        except IndexerNullVal:
            return True
