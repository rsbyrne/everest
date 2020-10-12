from functools import wraps
from collections import OrderedDict, namedtuple
import numpy as np

from ._producer import Producer, LoadFail, OutsNull
from ..comparator import Comparator, Prop
from ..anchor import NoActiveAnchorError
from ..reader import PathNotInFrameError
from ..value import Value

from ..exceptions import EverestException
class IndexerException(EverestException):
    pass
class IndexAlreadyLoaded(IndexerException):
    pass
class IndexerNullVal(IndexerException):
    pass
class IndexerLoadFail(LoadFail, IndexerException):
    pass
class IndexerLoadNull(IndexerLoadFail, IndexerNullVal):
    pass
class IndexerLoadRedundant(IndexerLoadFail):
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
        self.indices = namedtuple('IndexerHost', self.indexerKeys)(
            *self.indexers
            )
        self.i = self.indices
        super().__init__(**kwargs)

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
    def indexersInfo(self):
        return list(zip(
            self.indexers,
            self.indexerKeys,
            self.indexerTypes,
            ))

    def _get_metaIndex(self, arg):
        if type(arg) is Value:
            arg = arg.plain
        trueTypes = [issubclass(type(arg), t) for t in self.indexerTypes]
        if any(trueTypes):
            return trueTypes.index(True)
        else:
            raise TypeError(repr(arg)[:100], type(arg))
    def _get_indexInfo(self, arg):
        return self.indexersInfo[self._get_metaIndex(arg)]
    def _process_index(self, arg):
        i, ik, it = self._get_indexInfo(arg)
        if arg < 0.:
            return i - arg
        else:
            return arg
    def _indexer_process_endpoint(self, arg):
        i, ik, it = self._get_indexInfo(arg)
        return Comparator(
            Prop(self, 'indices', ik),
            self._process_index(arg),
            op = 'ge'
            )

    def _nullify_indexers(self):
        for indexer in self.indexers:
            indexer.value = None
    def _zero_indexers(self):
        for indexer in self.indexers:
            indexer.value = 0
    @property
    def _indexers_isnull(self):
        return any([i.null for i in self.indexers])
    @property
    def _indexers_iszero(self):
        if self._indexers_isnull:
            return False
        else:
            return any([i == 0 for i in self.indexers])
    @property
    def _indexers_ispos(self):
        return not (self._indexers_isnull or self._indexers_iszero)

    def _out(self):
        outs = super()._out()
        outs.update(OrderedDict(zip(
            self.indexerKeys,
            [OutsNull if i.null else i.value for i in self.indexers]
            )))
        return outs

    @property
    def indicesDisk(self):
        diskIndices = OrderedDict()
        for k in self.indexerKeys:
            diskIndices[k] = list(self.readouts[k])
        return diskIndices
    @property
    def indicesStored(self):
        storedIndices = OrderedDict()
        stored = dict(self.outs.zipstacked)
        for k in self.indexerKeys:
            storedIndices[k] = list(stored[k])
        return storedIndices
    @property
    def indicesAll(self):
        return self._indices_all()
    def _indices_all(self, clashes = False):
        combinedIndices = OrderedDict()
        try:
            diskIndices = self.indicesDisk
        except (NoActiveAnchorError, PathNotInFrameError):
            diskIndices = OrderedDict([k, []] for k in self.indexerKeys)
        storedIndices = self.indicesStored
        for k in self.indexerKeys:
            combinedIndices[k] = sorted(set(
                [*diskIndices[k], *storedIndices[k]]
                ))
        if clashes:
            clashes = OrderedDict()
            for k in self.indexerKeys:
                clashes[k] = sorted(set.intersection(
                    set(diskIndices[k]), set(storedIndices[k])
                    ))
            return combinedIndices, clashes
        else:
            return combinedIndices
    def _indexer_drop_clashes(self):
        _, clashes = self._indices_all(clashes = True)
        clashes = zip(*clashes.values())
        stored = zip(*[self.outs.stored[k] for k in self.indexerKeys])
        toDrop = []
        for i, row in enumerate(stored):
            if any([all([r == c for r in row]) for c in clashes]):
                toDrop.append(i)
        self.outs.drop(toDrop)

    def _save(self):
        self._indexer_drop_clashes()
        super()._save()

    def _load_process(self, outs):
        vals = [outs.pop(k) for k in self.indexerKeys]
        if any([v is OutsNull for v in vals]):
            raise IndexerLoadNull
        if [*vals] == [*self.indexers]:
            raise IndexerLoadRedundant
        for val, i in zip(vals, self.indexers):
            i.value = val
        return super()._load_process(outs)
    def _load(self, arg):
        try:
            i, ik, it = self._get_indexInfo(arg)
        except TypeError:
            return super()._load(arg)
        arg = self._process_index(arg)
        try:
            ind = self.outs.index(**{ik: arg})
        except ValueError:
            try:
                ind = self.indicesDisk[ik].index(arg)
            except (ValueError, NoActiveAnchorError, PathNotInFrameError):
                raise IndexerLoadFail
            return self._load_index_disk(ind)
        return self._load_index_stored(ind)
