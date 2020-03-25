import numpy as np
import time
from types import FunctionType

from .. import utilities
from .. import disk
from ..reader import Reader

from . import buffersize_exceeded
from ._getter import Getter
from . import anchorwrap
from ..weaklist import WeakList
from ..writer import ExtendableDataset
from ..exceptions import EverestException
from .. import mpi

class AbortStore(EverestException):
    pass

class Producer(Getter):

    def __init__(
            self,
            **kwargs
            ):

        self._pre_out_fns = WeakList()
        self._outFns = WeakList()
        self._post_out_fns = WeakList()
        self._pre_store_fns = WeakList()
        self._post_store_fns = WeakList()
        self._pre_save_fns = WeakList()
        self._post_save_fns = WeakList()
        self.outkeys = []
        self.stored = []

        super().__init__(**kwargs)

        # Getter attributes:
        self._get_fns.append(self._producer_get)

        # Built attributes:
        self._post_anchor_fns.append(self._producer_post_anchor)
        # self.localObjects['outputs'] = dict()

        self.set_autosave(True)
        self.set_save_interval(3600.)

    def set_autosave(self, val: bool):
        self.autosave = val
    def set_save_interval(self, val: float):
        self.saveinterval = val
    def get_stored_nbytes(self):
        nbytes = 0
        for datas in self.stored:
            for data in datas:
                nbytes += np.array(data).nbytes
        return nbytes

    @property
    def dataDict(self):
        processed = list(map(np.stack, (list(map(list, zip(*self.stored))))))
        return dict(zip(self.outkeys, processed))

    def out(self):
        for fn in self._pre_out_fns: fn()
        outs = tuple([item for fn in self._outFns for item in fn()])
        assert len(outs) == len(self.outkeys), \
            "Outkeys do not match outputs!"
        for fn in self._post_out_fns: fn()
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
        mpi.message(';')
        self.nbytes = self.get_stored_nbytes()
        if self.anchored and self.autosave:
            self._autosave()

    def clear(self):
        self.stored = []

    @anchorwrap
    @disk.h5filewrap
    def save(self):
        for fn in self._pre_save_fns: fn()
        self._save()
        self.clear()
        self.lastsaved = time.time()
        for fn in self._post_save_fns: fn()
        mpi.message(':')

    def _producer_post_anchor(self):
        self.readouts = Reader(self.name, self.path, self.hashID, 'outputs')
        self.save()

    def _save(self):
        wrappedDict = {
            key: ExtendableDataset(val) \
                for key, val in self.dataDict.items()
            }
        self.writer.add(wrappedDict, 'outputs', self.hashID)

    @anchorwrap
    def _autosave(self):
        if buffersize_exceeded():
            self.save()
        elif hasattr(self, 'lastsaved'):
            if time.time() - self.lastsaved > self.saveinterval:
                self.save()

    def _producer_get(self, arg):
        if type(arg) is str:
            return self._producer_get_str(arg)
        else:
            return None

    def _producer_get_str(self, key):
        if not key in self.outkeys:
            raise ValueError("That key is not valid for this producer.")
        if self.anchored:
            self.save()
            out = self.readouts[key]
        else:
            out = self.dataDict[key]
        return out
