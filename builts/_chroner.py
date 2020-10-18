import numpy as np

from ._indexer import Indexer, _indexer_load_wrapper, IndexerNullVal
from ..functions import Function

class Chroner(Indexer):

    _defaultChronsKey = 'chron'
    _defaultChronNullVal = float('nan')

    def __init__(self, **kwargs):
        self._chronNullVal = self._defaultChronNullVal
        self._chronsKey = self._defaultChronsKey
        self._chron = Function(
            self._chronNullVal,
            name = self._chronsKey,
            null = True
            )
        super().__init__(**kwargs)

    def _indexers(self):
        for o in super()._indexers(): yield o
        yield self._chron
    def _indexerKeys(self):
        for o in super()._indexerKeys(): yield o
        yield self._chronsKey
    def _indexerTypes(self):
        for o in super()._indexerTypes(): yield o
        yield (float, np.float)
