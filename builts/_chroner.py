import numpy as np
from functools import wraps

from ._indexer import Indexer, _indexer_load_wrapper
from ._producer import AbortStore, LoadFail
from ..value import Value
from ..anchor import NoActiveAnchorError

from .. import exceptions
class ChronerException(exceptions.EverestException):
    pass
class ChronAlreadyLoadedError(ChronerException):
    pass
class ChronerLoadFail(ChronerException, LoadFail):
    pass

class Chroner(Indexer):

    _defaultChronsKey = 'chron'
    _defaultNullVal = float('nan')

    def __init__(self, **kwargs):
        self._chronNullVal = self._defaultNullVal
        self.chron = Value(self._chronNullVal)
        self.chronsKey = self._defaultChronsKey
        super().__init__(**kwargs)

    def _indexers(self):
        for o in super()._indexers(): yield o
        yield self.chron
    def _indexerKeys(self):
        for o in super()._indexerKeys(): yield o
        yield self.chronsKey
    def _indexerTypes(self):
        for o in super()._indexerTypes(): yield o
        yield np.int
    def _indexerNulls(self):
        for o in super()._indexerNulls(): yield o
        yield self._chronNullVal

    def _outkeys(self):
        for o in super()._outkeys(): yield o
        yield self.chronsKey
    def _out(self):
        for o in super()._out(): yield o
        yield self.chron.value

    @property
    def _chronsKeyIndex(self):
        return self.outkeys.index(self.chronsKey)
    @property
    def chrons_stored(self):
        storedChrons = sorted([
            row[self._chronsKeyIndex] for row in self.stored
            ])
        assert sorted(set(storedChrons)) == storedChrons
        return storedChrons
    @property
    def chrons_disk(self):
        try:
            chrons = self.readouts[self.chronsKey]
            assert len(set(chrons)) == len(chrons)
            chrons = [int(x) for x in chrons]
            return chrons
        except (KeyError, NoActiveAnchorError):
            return []
    @property
    def chrons(self):
        return sorted(set([*self.chrons_stored, *self.chrons_disk]))
    def _chroner_sort_stored_fn(self):
        self.stored.sort(key = lambda row: row[self._chronsKeyIndex])
    def drop_chron(self, chron):
        del self.stored[self.chrons_stored.index(chron)]
    def _store(self):
        if self.chron in self.chrons_stored:
            raise AbortStore
        super()._store()

    def _save(self):
        keepChrons = [
            self.chrons_stored.index(i)
                for i in self.chrons_stored
                    if not i in self.chrons_disk
            ]
        self.stored[:] = [self.stored[i] for i in keepChrons]
        super()._save()

    @_indexer_load_wrapper
    def load_chron_stored(self, chron):
        return self.load_index_stored(self.chrons_stored.index(chron))
    @_indexer_load_wrapper
    def load_chron_disk(self, chron):
        return self.load_index_disk(self.chrons_disk.index(chron))
    def load_chron(self, chron):
        try:
            return self.load_chron_stored(chron)
        except ValueError:
            return self.load_chron_disk(chron)
    def _load_process(self, outs):
        outs = super()._load_process(outs)
        self.chron.value = outs.pop(self.chronsKey)
        return outs
    def _load(self, arg):
        i, ik, it, i0 = self._get_indexInfo(arg)
        if i is self.chron:
            try:
                self.load_chron(arg)
            except ValueError:
                raise ChronerLoadFail
        else:
            super()._load(arg)

    def _nullify_chron(self):
        self.chron.value = self._chronNullVal
    @property
    def _chron_isNull(self):
        try:
            self._process_index(self.chron.value)
            return False
        except IndexerNullVal:
            return True
