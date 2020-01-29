from .. import disk

from .producer import Producer

class Iterator(Producer):

    def __init__(self, initialiseFn, iterateFn, outFn, outkeys, loadFn, **kwargs):
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
        super().__init__(outFn, outkeys, **kwargs)
        self.initialise()

    def _initialise_wrap(self, initialise):
        self.count.value = 0
        initialise()

    def _iterate_wrap(self, iterate, n):
        for i in range(n):
            self.count.value += 1
            iterate()
            if any(self.consignments):
                self.store()

    def _load_wrap(self, load, count):
        if not self.count() == count:
            loadDict = self._load_dataDict(count)
            load(loadDict)
            self.count.value = count

    def _load_dataDict(self, count):
        if count in self.counts_stored:
            return self._load_dataDict_stored(count)
        else:
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

    @disk.h5filewrap
    def _load_dataDict_saved(self, count):
        self._check_anchored()
        # self.save()
        loadDict = {}
        counts = self.h5file[self.hashID]['outs']['_counts_']
        iterNo = 0
        while True:
            if iterNo >= len(counts):
                raise Exception("Count not found!")
            if counts[iterNo] == count:
                break
            iterNo += 1
        loadDict = {}
        for key in self.outkeys:
            loadData = self.h5file[self.hashID]['outs'][key][iterNo]
            loadDict[key] = loadData
        return loadDict

### EXAMPLE ###

from ..value import Value

class ExampleIterator(Iterator):
    # Implements the Bailey-Borwein-Plouffe formula;
    # default args yield pi.
    def __init__(
            self,
            s : int = 1,
            b : int = 16,
            A : list = [4, 0, 0, -2, -1, -1, 0, 0]
            ):
        self.state = Value(0.)
        self.kth = lambda k: 1. / b **k * sum([a / (len(A) * k + (j + 1))**s for j, a in enumerate(A)])
        super().__init__(
            self.initialise,
            self.iterate,
            self.out,
            ['pi',],
            self.load
            )
    def out(self):
        return [self.state.value,]
    def initialise(self):
        self.state.value = self.kth(0)
    def iterate(self):
        kthVal = self.kth(self.count.value)
        self.state.value += kthVal
    def load(self, loadDict):
        self.state.value = loadDict['pi']

CLASS = ExampleIterator
build = CLASS.build
