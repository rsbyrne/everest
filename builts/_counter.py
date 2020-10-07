import numpy as np

from ._indexer import Indexer, _indexer_load_wrapper, IndexerNullVal
from ..value import Value

class Counter(Indexer):

    _defaultCountsKey = 'count'
    _defaultCountNullVal = -999999999

    def __init__(self, **kwargs):
        self._countNullVal = self._defaultCountNullVal
        self._count = Value(self._countNullVal, null = True)
        self._countsKey = self._defaultCountsKey
        super().__init__(**kwargs)

    def _indexers(self):
        for o in super()._indexers(): yield o
        yield self._count
    def _indexerKeys(self):
        for o in super()._indexerKeys(): yield o
        yield self._countsKey
    def _indexerTypes(self):
        for o in super()._indexerTypes(): yield o
        yield np.int
