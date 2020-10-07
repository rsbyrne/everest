import numpy as np

from ._indexer import Indexer, _indexer_load_wrapper, IndexerNullVal
from ..value import Value

class Chroner(Indexer):

    _defaultChronsKey = 'chron'
    _defaultChronNullVal = float('nan')

    def __init__(self, **kwargs):
        self._chronNullVal = self._defaultChronNullVal
        self._chron = Value(self._chronNullVal, null = True)
        self._chronsKey = self._defaultChronsKey
        super().__init__(**kwargs)

    def _indexers(self):
        for o in super()._indexers(): yield o
        yield self._chron
    def _indexerKeys(self):
        for o in super()._indexerKeys(): yield o
        yield self._chronsKey
    def _indexerTypes(self):
        for o in super()._indexerTypes(): yield o
        yield np.float
