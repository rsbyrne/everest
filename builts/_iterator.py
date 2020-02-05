import numpy as np
from types import FunctionType

from .. import disk
from ._counter import Counter
from ._cycler import Cycler
from ._producer import make_dataDict
from .. import exceptions

class Iterator(Counter, Cycler):

    def __init__(
            self,
            initialiseFn : FunctionType = None,
            iterateFn : FunctionType = None,
            outFn : FunctionType = None,
            outkeys : list = None,
            loadFn : FunctionType = None,
            **kwargs
            ):

        self.initialise = lambda: self._initialise_wrap(
            initialiseFn,
            )
        self.initialised = False
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

        # Producer attributes:
        self.outFns.append(outFn)
        self.outkeys.extend(outkeys)
        self.samples.extend(
            [np.array([data,]) for data in outFn()]
            )
        self.indexKey = '_count_'
        self.dataKeys = [
            key for key in self.outkeys if not key == self.indexKey
            ]

        # Cycler attributes:
        self._cycle_fns.append(self.iterate)

        # Built attributes:
        def _post_anchor():
            self.h5filename = self.writer.h5filename
        self._iterator_post_anchor = _post_anchor
        self._post_anchor_fns.append(self._iterator_post_anchor)

        self.initialise()

    def _initialise_wrap(self, initialise):
        self.count.value = 0
        initialise()
        self.initialised = True

    def _iterate_wrap(self, iterate, n):
        if not self.initialised:
            self.initialise()
        for i in range(n):
            self.count.value += 1
            iterate()

    def _load_wrap(self, load, count):
        self.initialised = True
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
