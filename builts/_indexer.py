from functools import wraps
import numpy as np

from ._producer import Producer
from ..comparator import Comparator, Prop

from ..exceptions import EverestException
class IndexerException(EverestException):
    pass
class IndexAlreadyLoaded(IndexerException):
    pass
class IndexerNullVal(IndexerException):
    pass

def _indexer_load_wrapper(func):
    @wraps(func)
    def wrapper(self, arg, *args, **kwargs):
        index = self._process_index(arg)
        return func(self, index, *args, **kwargs)
    return wrapper

class Indexer(Producer):

    def __init__(self,
            **kwargs
            ):
        super().__init__(**kwargs)

    @property
    def indexer(self):
        ind = self.indexers
        assert len(ind)
        if len(ind) == 1:
            return ind[0]
        else:
            return ind
    @property
    def indexers(self):
        return tuple([*self._indexers()][1:])
    def _indexers(self):
        yield None
    @property
    def indexerKeys(self):
        return [*self._indexerKeys()][1:]
    def _indexerKeys(self):
        yield None
    @property
    def indexerTypes(self):
        return [*self._indexerTypes()][1:]
    def _indexerTypes(self):
        yield None
    @property
    def indexerNulls(self):
        return [*self._indexerNulls()][1:]
    def _indexerNulls(self):
        yield None
    @property
    def indexersInfo(self):
        return list(zip(
            self.indexers,
            self.indexerKeys,
            self.indexerTypes,
            self.indexerNulls,
            ))

    def _get_metaIndex(self, arg):
        return [issubclass(type(arg), t) for t in self.indexerTypes].index(True)
    def _get_indexInfo(self, arg):
        return self.indexersInfo[self._get_metaIndex(arg)]
    def _indexer_process_endpoint(self, arg):
        i, ik, it, i0 = self._get_indexInfo(arg)
        return Comparator(
            Prop(self, ik),
            self._process_index(arg),
            op = 'ge'
            )
    def _process_index(self, arg):
        if not issubclass(type(arg), (np.int, np.float)):
            raise TypeError(arg, type(arg))
        i, ik, it, i0 = self._get_indexInfo(arg)
        if arg == i0 or not arg < np.inf: # hence is null:
            raise IndexerNullVal
        elif arg < 0.:
            return i - arg
        else:
            return arg

    def _nullify_indexers(self):
        for i, ik, it, i0 in self.indexersInfo:
            i.value = i0
