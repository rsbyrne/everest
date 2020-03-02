import numpy as np
import time
from types import FunctionType

from .. import utilities
from .. import disk

from . import buffersize_exceeded
from . import Built
from ..weaklist import WeakList
from ..writer import ExtendableDataset
from ..exceptions import EverestException

class AbortStore(EverestException):
    pass

def make_dataDict(outkeys, stored):
    return dict(zip(outkeys, list(map(list, zip(*stored)))))

class Producer(Built):

    autosave = True
    saveinterval = 3600. # seconds

    def __init__(
            self,
            **kwargs
            ):

        self._outFns = WeakList()
        self._pre_store_fns = WeakList()
        self._post_store_fns = WeakList()
        self._pre_save_fns = WeakList()
        self._post_save_fns = WeakList()
        self.outkeys = []
        self.stored = []

        super().__init__(**kwargs)

    def set_autosave(self, val: bool):
        self.autosave = val
    def set_saveinterval(self, val: float):
        self.saveinterval = val
    def get_stored_nbytes(self):
        nbytes = 0
        for datas in self.stored:
            for data in datas:
                nbytes += np.array(data).nbytes
        return nbytes

    def make_dataDict(self):
        processed = list(map(np.stack, (list(map(list, zip(*self.stored))))))
        return dict(zip(self.outkeys, processed))

    def out(self):
        outs = tuple([item for fn in self._outFns for item in fn()])
        assert len(outs) == len(self.outkeys), \
            "Outkeys do not match outputs!"
        return outs

    def store(self):
        try:
            self._store()
        except AbortStore:
            pass

    def _store(self):
        for fn in self._pre_store_fns: fn()
        self.stored.append(self.out())
        for fn in self._post_store_fns: fn()
        self.nbytes = self.get_stored_nbytes()
        if self.autosave:
            self._autosave()

    def clear(self):
        self.stored = []

    def save(self):
        for fn in self._pre_save_fns: fn()
        self._check_anchored()
        self._save()
        self.clear()
        self.lastsaved = time.time()
        for fn in self._post_save_fns: fn()

    def _save(self):
        wrappedDict = {
            key: ExtendableDataset(val) \
                for key, val in self.make_dataDict().items()
            }
        self.writer.add(wrappedDict, 'outputs', self.hashID)

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
                self._check_anchored()
                self.save()
