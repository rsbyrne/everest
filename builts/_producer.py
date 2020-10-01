import os
import numpy as np
import time
from types import FunctionType, MethodType

from .. import utilities
from .. import disk
from ..reader import Reader
from ..writer import Writer

from . import buffersize_exceeded
from ._promptable import Promptable
from . import anchorwrap
from ..weaklist import WeakList
from ..array import EverestArray
from ..exceptions import EverestException
from .. import mpi

class AbortStore(EverestException):
    pass

class _DataProxy:
    def __init__(self, method):
        self._method = method
    def __getitem__(self, inp):
        return self._method(inp)

class Producer(Promptable):

    def __init__(
            self,
            baselines = dict(),
            **kwargs
            ):

        self._outputRootKey = self.hashID
        self._outputMasterKeys = WeakList([self._producer_outputMasterKey,])
        self._outputSubKeys = WeakList()

        self.baselines = dict()
        for key, val in sorted(baselines.items()):
            self.baselines[key] = EverestArray(val, extendable = False)

        self._pre_out_fns = WeakList()
        self._outFns = WeakList()
        self._post_out_fns = WeakList()
        self._pre_store_fns = WeakList()
        self._post_store_fns = WeakList()
        self._pre_save_fns = WeakList()
        self._post_save_fns = WeakList()
        self._producer_outkeys = WeakList()
        self._stored = dict()

        super().__init__(baselines = self.baselines, **kwargs)

        # Promptable attributes:
        self._prompt_fns.append(self._producer_prompt)

        # Built attributes:
        self._post_anchor_fns.append(self._producer_post_anchor)

        self.set_autosave(True)
        self.set_save_interval(3600.)

    def _producer_outputMasterKey(self):
        return 'outputs'
    @property
    def _outputMasterKey(self):
        return '/'.join([fn() for fn in self._outputMasterKeys])
    @property
    def _outputSubKey(self):
        return '/'.join([fn() for fn in self._outputSubKeys])
    @property
    def _outputKey(self):
        keys = [self._outputRootKey, self._outputMasterKey, self._outputSubKey]
        return '/'.join([k for k in keys if len(k)])

    @property
    def outkeys(self):
        out = []
        for item in self._producer_outkeys:
            if callable(item):
                item = item()
            if type(item) is str:
                out.append(item)
            else:
                try:
                    out.extend(item)
                except TypeError:
                    out.append(item)
        return out

    def _producer_prompt(self, prompter):
        self.store()

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

    @property
    def stored(self):
        key = self._outputSubKey
        if not key in self._stored:
            self._stored[key] = []
        return self._stored[key]

    def out(self):
        for fn in self._pre_out_fns: fn()
        outs = tuple([item for fn in self._outFns for item in fn()])
        assert len(outs) == len(self.outkeys), \
            ("Outkeys do not match outputs!", (len(outs), len(self.outkeys)))
        for fn in self._post_out_fns: fn()
        return outs
    @property
    def outDict(self):
        return dict(zip(self.outkeys, self.out()))

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
        self._stored[self._outputSubKey].clear()

    @anchorwrap
    @disk.h5filewrap
    def save(self):
        for fn in self._pre_save_fns: fn()
        self._save()
        self.clear()
        self.lastsaved = time.time()
        for fn in self._post_save_fns: fn()
        mpi.message(':')

    @property
    @anchorwrap
    def readouts(self):
        return Reader(
            self.name,
            self.path,
            self._outputKey
            )
    @property
    @anchorwrap
    def writeouts(self):
        return Writer(
            self.name,
            self.path,
            self._outputKey
            )

    def _producer_post_anchor(self):
        self.save()

    def _save(self):
        wrappedDict = dict()
        for key, val in sorted(self.dataDict.items()):
            wrappedDict[key] = EverestArray(
                val,
                extendable = True,
                indices = '/'.join([self._outputKey, self._countsKey])
                )
        self.writeouts.add_dict(wrappedDict)

    @anchorwrap
    def _autosave(self):
        if buffersize_exceeded():
            self.save()
        elif hasattr(self, 'lastsaved'):
            if time.time() - self.lastsaved > self.saveinterval:
                self.save()

    # def _producer_get(self, arg):
    #     if type(arg) is str:
    #         key = arg
    #         if not key in self.outkeys:
    #             raise ValueError("That key is not valid for this producer.")
    #         if self.anchored:
    #             self.save()
    #             out = self.readouts[key]
    #         else:
    #             out = self.dataDict[key]
    #         return out
    #     elif type(arg) is tuple:
    #         tup = arg
    #         return [self._producer_get(k) for k in tup]
    #     else:
    #         raise TypeError("Input must be string or tuple.")
    #
    # @property
    # def data(self):
    #     return _DataProxy(self._producer_get)
