import numpy as np
import time
from types import FunctionType

from .. import utilities
from .. import disk

from . import buffersize_exceeded
from ._mutators import Mutator

class Producer(Mutator):

    autosave = True
    saveinterval = 3600. # seconds

    def __init__(
            self,
            **kwargs
            ):

        self.outFns = []
        self._pre_store_fns = []
        self._post_store_fns = []
        self._pre_save_fns = []
        self._post_save_fns = []
        self.outkeys = []
        self.samples = []
        self.stored = []

        super().__init__(**kwargs)

        self._pre_anchor_fns.append(lambda: \
            self.localObjects.update({
                key: val \
                    for key, val in zip(self.outkeys, self.samples)
                })
            )

        def _update_mutateDict():
            outs = list(map(list, zip(*self.stored)))
            self._mutateDict.update({
                key: np.array(val, dtype = utilities._obtain_dtype(val[0])) \
                    for key, val in zip(self.outkeys, outs)
                })
        self._update_mutateDict_fns.append(_update_mutateDict)

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
