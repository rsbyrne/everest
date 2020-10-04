import numpy as np
from functools import wraps

from ._producer import Producer, AbortStore, LoadFail
from ..value import Value
from ..anchor import NoActiveAnchorError

from .. import exceptions
class CounterException(exceptions.EverestException):
    pass
class CountAlreadyLoadedError(CounterException):
    pass
class CounterLoadFail(CounterException, LoadFail):
    pass

class Counter(Producer):

    _defaultCountsKey = 'count'

    def __init__(self, **kwargs):
        self.count = Value(-1)
        self.countsKey = self._defaultCountsKey
        super().__init__(**kwargs)

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

    def _process_load_count_arg(self, count):
        if count == self.count:
            raise CountAlreadyLoadedError
        elif count < 0:
            if self.initialised:
                count += self.count
            else:
                count = -count
            return count
        else:
            return count
    def _counter_load_wrapper(func):
        @wraps(func)
        def wrapper(self, count, *args, **kwargs):
            count = self._process_load_count_arg(count)
            return func(self, count, *args, **kwargs)
        return wrapper
    @_counter_load_wrapper
    def load_count_stored(self, count):
        return self.load_index_stored(self.counts_stored.index(count))
    @_counter_load_wrapper
    def load_count_disk(self, count):
        return self.load_index_disk(self.counts_disk.index(count))
    def load_count(self, count):
        try:
            return self.load_count_stored(count)
        except ValueError:
            return self.load_count_disk(count)
    def _load_process(self, outs):
        outs = super()._load_process(outs)
        self.count.value = outs.pop(self.countsKey)
        return outs
    def _load(self, arg):
        if issubclass(type(arg), np.int):
            try:
                self.load_count(arg)
            except ValueError:
                raise CounterLoadFail
        else:
            super()._load(arg)
