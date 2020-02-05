import numpy as np
import time
from types import FunctionType

from .. import utilities
from .. import disk

from . import buffersize_exceeded
from ._mutators import Mutator
from ..weaklist import WeakList

def make_dataDict(outkeys, stored):
    return dict(zip(outkeys, list(map(list, zip(*stored)))))

class Producer(Mutator):

    autosave = True
    saveinterval = 3600. # seconds

    def __init__(
            self,
            **kwargs
            ):

        self.outFns = WeakList()
        self._pre_store_fns = WeakList()
        self._post_store_fns = WeakList()
        self._pre_save_fns = WeakList()
        self._post_save_fns = WeakList()
        self.outkeys = []
        self.samples = []
        self.stored = []

        super().__init__(**kwargs)

        self._producer_pre_anchor_fn = \
            lambda: self.localObjects.update({
                key: val \
                    for key, val in zip(self.outkeys, self.samples)
                })
        self._pre_anchor_fns.append(self._producer_pre_anchor_fn)

        self._producer_update_mutateDict_fn = \
            lambda: self._mutateDict.update(self.make_dataDict())
        self._update_mutateDict_fns.append(self._producer_update_mutateDict_fn)

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
        outs = tuple([item for fn in self.outFns for item in fn()])
        assert len(outs) == len(self.outkeys)
        return outs

    def store(self):
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
        if len(self.stored) > 0:
            self.mutate()
            self.clear()
            self.lastsaved = time.time()
        for fn in self._post_save_fns: fn()

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
