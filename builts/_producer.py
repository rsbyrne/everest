import numpy as np
import time
from functools import wraps
from collections import OrderedDict

from .. import disk
from ..reader import Reader
from ..writer import Writer

from . import buffersize_exceeded
from ._promptable import Promptable
from ..array import EverestArray
from .. import exceptions
from .. import mpi

class ProducerException(exceptions.EverestException):
    pass
class LoadFail(ProducerException):
    pass
class ProducerLoadFail(LoadFail):
    pass
class AbortStore(ProducerException):
    pass
# class ProducerMissingMethod(exceptions.MissingMethod):
#     pass

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

        self.outputRootKey = self.hashID

        self.baselines = dict()
        for key, val in sorted(baselines.items()):
            self.baselines[key] = EverestArray(val, extendable = False)

        self._stored = dict()

        super().__init__(baselines = self.baselines, **kwargs)

        # Promptable attributes:
        self._prompt_fns.append(self._producer_prompt)

        self.set_autosave(True)
        self.set_save_interval(3600.)

    @property
    def outputMasterKey(self):
        return '/'.join([k for k in self._outputMasterKey if len(k)])
    def _outputMasterKey(self):
        yield 'outputs'
    @property
    def outputSubKey(self):
        return '/'.join([k for k in self._outputSubKey if len(k)])
    def _outputSubKey(self):
        yield ''
    @property
    def outputKey(self):
        keys = [self.outputRootKey, self.outputMasterKey, self.outputSubKey]
        return '/'.join([k for k in keys if len(k)])

    @property
    def outkeys(self):
        return [*self._outkeys()][1:]
    def _outkeys(self):
        yield None
    @property
    def out(self):
        return [*self._out()][1:]
    def _out(self):
        yield None
    @property
    def outDict(self):
        return OrderedDict(zip(self.outkeys, self.out))

    def _producer_prompt(self, prompter):
        self.store()

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
    def store(self):
        try:
            self._store()
        except AbortStore:
            pass
    def _store(self):
        self.stored.append(self.out)
        mpi.message(';')
        self.nbytes = self.get_stored_nbytes()
        if self.anchored and self.autosave:
            self._autosave()
    def clear(self):
        self._stored[self._outputSubKey].clear()

    @property
    def readouts(self):
        return Reader(
            self.name,
            self.path,
            self._outputKey
            )
    @property
    def writeouts(self):
        return Writer(
            self.name,
            self.path,
            self._outputKey
            )

    @disk.h5filewrap
    def save(self):
        self._save()
        self.lastsaved = time.time()
        self.clear()
        mpi.message(':')
    def _save(self):
        self.writeouts.add(self, 'producer')
        wrappedDict = dict()
        for key, val in sorted(self.dataDict.items()):
            wrappedDict[key] = EverestArray(
                val,
                extendable = True,
                # indices = '/'.join([self.outputKey, self.countsKey])
                )
        self.writeouts.add_dict(wrappedDict)
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
    def _autosave(self):
        if buffersize_exceeded():
            self.save()
        elif hasattr(self, 'lastsaved'):
            if time.time() - self.lastsaved > self.saveinterval:
                self.save()

    def _producer_load_wrapper(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return self._load_process(func(self, *args, **kwargs))
        return wrapper
    def _load_process(self, outs):
        return OrderedDict(zip(self.outkeys, outs))
    @_producer_load_wrapper
    def load_index_stored(self, index):
        return self.stored[index]
    @_producer_load_wrapper
    def load_index_disk(self, index):
        return [
            self.readouts[key][index]
                for key in self.outkeys
                ]
    def load_index(self, index):
        try:
            return self.load_index_stored(index)
        except IndexError:
            return self.load_index_disk(index)
    def _load(self, arg):
        try:
            return self.load_index(arg)
        except IndexError:
            raise ProducerLoadFail
    def load(self, arg):
        return self._load(arg)
