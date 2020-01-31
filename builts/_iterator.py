import numpy as np
from types import FunctionType

from everest import disk
from everest.builts._counter import Counter
from everest.builts._producer import Producer
from everest.builts._producer import make_dataDict
from everest import exceptions

class Iterator(Counter, Producer):

    def __init__(
            self,
            initialiseFn : FunctionType,
            iterateFn : FunctionType,
            outFn : FunctionType,
            outkeys : list,
            loadFn : FunctionType,
            **kwargs
            ):
        self.initialise = lambda: self._initialise_wrap(
            initialiseFn,
            )
        self.iterate = lambda n = 1: self._iterate_wrap(
            iterateFn,
            n,
            )
        self.load = lambda count: self._load_wrap(
            loadFn,
            count
            )
        self.reset = self.initialise
        super().__init__(**kwargs)
        self.outFns.append(outFn)
        self.outkeys.extend(outkeys)
        self.samples.extend(
            [np.array([data,]) for data in outFn()]
            )
        self.indexKey = '_count_'
        self.dataKeys = [
            key for key in self.outkeys if not key == self.indexKey
            ]
        def _post_anchor():
            self.h5filename = self.writer.h5filename
        self._post_anchor_fns.append(_post_anchor)
        self.initialise()

    def _initialise_wrap(self, initialise):
        self.count.value = 0
        initialise()

    def _iterate_wrap(self, iterate, n):
        for i in range(n):
            self.count.value += 1
            iterate()

    def _load_wrap(self, load, count):
        if not self.count() == count:
            loadDict = self._load_dataDict(count)
            load(loadDict)
            self.count.value = count

    def _load_dataDict(self, count):
        if count in self.counts_stored:
            return self._load_dataDict_stored(count)
        elif self.anchored:
            return self._load_dataDict_saved(count)

    def _load_dataDict_stored(self, count):
        dataDict = self.make_dataDict()
        counts = dataDict[self.indexKey]
        index = np.where(counts == count)[0][0]
        datas = [dataDict[key] for key in self.dataKeys]
        return dict(zip(self.dataKeys, [data[index] for data in datas]))

    def _load_dataDict_saved(self, count):
        self._check_anchored()
        counts = self.reader[self.hashID, self.indexKey]
        matches = np.where(counts == count)[0]
        assert len(matches) <= 1
        if len(matches) == 0:
            print(matches)
            raise exceptions.CountNotOnDiskError
        else:
            index = matches[0]
        datas = [self.reader[self.hashID, key] for key in self.dataKeys]
        return dict(zip(self.dataKeys, [data[index] for data in datas]))

from .examples import pimachine as example
