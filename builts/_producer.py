import numpy as np
import time
from types import FunctionType

from .. import utilities
from .. import disk

from . import buffersize_exceeded
from ._counter import Counter
from ._mutators import Mutator

class Producer(Mutator, Counter):

    autosave = True
    saveinterval = 3600. # seconds

    def __init__(
            self,
            outFn : FunctionType,
            outkeys : list,
            **kwargs
            ):

        self.out = lambda: self._out_wrap(outFn)
        samples = self.out()
        mutateDict = {
            key: np.array([data,]) \
                for key, data in zip(outkeys, samples)
            }
        mutateDict['_counts_'] = np.array([1,], dtype = np.int8)

        self.outkeys = outkeys
        self.stored = []
        self.counts_stored = []
        self.counts_disk = []
        self.counts_captured = []

        def update_mutateDict():
            counts, outs = zip(*self.stored)
            mutateDict.update({
                key: np.array(val, dtype = utilities._obtain_dtype(val[0])) \
                    for key, val in zip(self.outkeys, zip(*outs))
                })
            mutateDict['_counts_'] = np.array(counts, dtype = 'i8')

        super().__init__(
            mutateDict = mutateDict,
            update_MutateDict = update_mutateDict,
            **{**mutateDict, **kwargs}
            )

    def set_autosave(self, val: bool):
        self.autosave = val
    def set_saveinterval(self, val: float):
        self.saveinterval = val
    def get_stored_nbytes(self):
        nbytes = 0
        for count in self.stored:
            for data in count[1]:
                nbytes += np.array(data).nbytes
        return nbytes

    def _out_wrap(self, out):
        return out()

    def store(self):
        vals = self.out()
        count = self.count()
        if not count in self.counts_captured:
            entry = [count, vals]
            self.stored.append(entry)
            self.stored.sort()
        self._update_counts()
        self.nbytes = self.get_stored_nbytes()
        if self.autosave:
            self._autosave()

    def clear(self):
        self.stored = []
        self.counts_stored = []

    def save(self):
        self._check_anchored()
        if len(self.stored) > 0:
            self.mutate()
            self.clear()
            self._update_counts()
            self.lastsaved = time.time()

    def _autosave(self):
        if buffersize_exceeded():
            if self.anchored:
                self.save()
            else:
                raise Exception(
                    "Buffersize has been exceeded, \n\
                    but no save destination has been provided \n\
                    to dump the data."
                    )
        elif hasattr(self, 'lastsaved'):
            if time.time() - self.lastsaved > self.saveinterval:
                if self.anchored:
                    self.save()

    def _update_counts(self):
        if self.anchored:
            counts = self.reader[self.hashID, '_counts_']
            self.counts_disk = list(set(counts))
        self.counts_stored = utilities.unique_list(
            [index for index, data in self.stored]
            )
        self.counts_captured = utilities.unique_list(
            [*self.counts_stored, *self.counts_disk]
            )
