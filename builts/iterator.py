from .. import disk

from .producer import Producer

class Iterator(Producer):

    def __init__(self, initialiseFn, iterateFn, outFn, outkeys, loadFn):
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
        super().__init__(outFn, outkeys)
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
