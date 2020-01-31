import numpy as np
from types import FunctionType

from everest import disk
from everest.builts._counter import Counter
from everest.builts._producer import Producer
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
        def _post_anchor():
            self.h5filename = self.writer.h5filename
        self._post_anchor_fns.append(_post_anchor)
        self.initialise()

    def _initialise_wrap(self, initialise):
        self.count = 0
        initialise()

    def _iterate_wrap(self, iterate, n):
        for i in range(n):
            self.count += 1
            iterate()

    def _load_wrap(self, load, count):
        if not self.count == count:
            loadDict = self._load_dataDict(count)
            load(loadDict)
            self.count = count

    def _load_dataDict(self, count):
        if count in self.counts_stored:
            return self._load_dataDict_stored(count)
        elif self.anchored:
            return self._load_dataDict_saved(count)

    def _load_dataDict_stored(self, count):
        storedDict = {
            count: data for count, data in self.stored
            }
        loadData = storedDict[count]
        loadDict = {
            outkey: data \
                for outkey, data in zip(
                    self.outkeys,
                    loadData
                    )
            }
        return loadDict

    def _load_dataDict_saved(self, count):
        self._check_anchored()
        loadDict = {}
        counts = self.reader[self.hashID, '_count_']
        matches = np.where(counts == count)[0]
        assert len(matches) <= 1
        if len(matches) == 0:
            raise exceptions.CountNotOnDiskError
        index = np.where(counts == count)[0][0]
        dataKeys = [key for key in self.outkeys if not key == '_count_']
        return {key: self.reader[self.hashID, key] for key in dataKeys}

from .examples.pimachine import PiMachine as Example
