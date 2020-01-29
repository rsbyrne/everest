import numpy as np
import time

from .. import utilities
from .. import disk

from . import buffersize_exceeded
from ._counter import Counter

class Producer(Counter):

    autosave = True
    saveinterval = 3600. # seconds

    def __init__(self, outFn, outkeys, **kwargs):
            out = self.out
            self.out = lambda: self._out_wrap(
                outFn
                )
            self.outkeys = outkeys
            self.stored = []
            self.dataDict = {}
            self.counts_stored = []
            self.counts_disk = []
            self.counts_captured = []
            self.consignments = set()
            super().__init__(**kwargs)

    def set_autosave(self, val: bool):
        self.autosave = val

    def set_saveinterval(self, val: float):
        self.saveinterval = val

    def add_consignment(self, consignment):
        self.consignments.add(consignment)

    def remove_consignment(self, consignment):
        self.consignments.remove(consignment)

    def _out_wrap(self, out):
        return out()

    def get_stored_nbytes(self):
        nbytes = 0
        for count in self.stored:
            for data in count[1]:
                nbytes += np.array(data).nbytes
        return nbytes

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

    def _update_dataDict(self):
        counts, outs = zip(*self.stored)
        self.dataDict.update({
            key: np.array(val, dtype = utilities._obtain_dtype(val[0])) \
                for key, val in zip(self.outkeys, zip(*outs))
            })
        self.dataDict['_counts_'] = np.array(counts, dtype = 'i8')

    def save(self):
        self._check_anchored()
        if len(self.stored) == 0:
            return None
        self._update_dataDict()
        for key in ['_counts_', *self.outkeys]:
            self._add_dataset(
                self.dataDict[key],
                key,
                [self.hashID, 'outs',]
                )
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
            self.counts_disk = self._get_disk_counts()
        self.counts_stored = utilities.unique_list(
            [index for index, data in self.stored]
            )
        self.counts_captured = utilities.unique_list(
            [*self.counts_stored, *self.counts_disk]
            )

    @disk.h5filewrap
    def _get_disk_counts(self):
        counts_disk = []
        selfgroup = self.h5file[self.hashID]
        if 'outs' in selfgroup:
            outsgroup = selfgroup['outs']
            if '_counts_' in outsgroup:
                counts = outsgroup['_counts_']
                counts_disk.extend(utilities.unique_list(list(counts[...])))
        return counts_disk
