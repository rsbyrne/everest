import numpy as np
from types import FunctionType

from .. import disk
from ._counter import Counter
from ._cycler import Cycler
from ._producer import Producer
from ._producer import make_dataDict
from .. import exceptions

class Iterator(Counter, Cycler):
# class Iterator(Producer):
# class Iterator(Cycler):

    def __init__(
            self,
            **kwargs
            ):

        self.initialised = False

        super().__init__(**kwargs)

        # Producer attributes:
        self._outFns.append(self._out)
        self.outkeys.extend(self._outkeys)
        self.samples.extend(
            [np.array([data,]) for data in self.out()]
            )
        self.indexKey = '_count_'
        self.dataKeys = [
            key for key in self.outkeys if not key == self.indexKey
            ]

        # Cycler attributes:
        self._cycle_fns.append(self.iterate)

        # Built attributes:
        self._post_anchor_fns.append(self._iterator_post_anchor)

        self.initialise()

    def _iterator_post_anchor(self):
        self.h5filename = self.writer.h5filename

    def initialise(self):
        self.count.value = 0
        self._initialise()
        self.initialised = True

    def reset(self):
        self.initialise()

    def iterate(self, n = 1):
        if not self.initialised:
            self.initialise()
        for i in range(n):
            self.count += 1
            self._iterate()

    def load(self, count):
        self.initialised = True
        if not self.count() == count:
            loadDict = self._load_dataDict(count)
            self._load(loadDict)
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
