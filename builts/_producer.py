import numpy as np
import random
import math
import time
from functools import wraps
from collections.abc import Mapping
from collections import OrderedDict

from .. import disk
from ..reader import Reader
from ..writer import Writer

# from . import buffersize_exceeded
from ._promptable import Promptable
from ..array import EverestArray
from .. import exceptions
from ..utilities import Grouper, prettify_nbytes

class ProducerException(exceptions.EverestException):
    pass
class ProducerNoOuts(ProducerException):
    pass
class ProducerIOError(ProducerException):
    pass
class SaveFail(ProducerIOError):
    pass
class LoadFail(ProducerIOError):
    pass
class ProducerSaveFail(SaveFail):
    pass
class ProducerLoadFail(LoadFail):
    pass
class ProducerNothingToSave(ProducerSaveFail):
    pass
class AbortStore(ProducerException):
    pass
# class ProducerMissingMethod(exceptions.MissingMethod):
#     pass

from collections import OrderedDict
import numpy as np
import math

from everest.utilities import make_hash
from everest.builts._producer import ProducerException

class OutsException(ProducerException):
    pass
class OutsAlreadyStored(OutsException):
    pass
class OutsAlreadyCleared(OutsException):
    pass
class NullValueDetected(OutsException):
    pass
class OutsNull:
    pass

class Outs:
    def __init__(self, keys, name = 'default'):
        self._keys, self.name = keys, name
        self.data = OrderedDict([(k, OutsNull) for k in self._keys])
        self.stored = OrderedDict([(k, []) for k in self._keys])
        self.hashVals = []
        self.n = 0
        self.token = 0
    def update(self, outs, silent = False):
        if any([v is OutsNull for v in outs.values()]):
            if not silent:
                raise NullValueDetected
        for k, v in outs.items():
            self[k] = v
    def __setitem__(self, k, v):
        if k in self._keys:
            self.data[k] = v
            setattr(self, k, v)
        else:
            raise OutsKeysImmutable
    def __getitem__(self, k):
        return self.data[k]
    def __delitem__(self, k):
        raise OutsKeysImmutable
    def store(self, silent = False):
        hashVal = make_hash(self.data.values())
        if hashVal in self.hashVals:
            if not silent:
                raise OutsAlreadyStored
        else:
            if any([v is OutsNull for v in self.data.values()]):
                if silent:
                    pass
                else:
                    raise NullValueDetected
            else:
                for k, v in self.data.items():
                    self.stored[k].append(v)
                self.hashVals.append(hashVal)
                self.n += 1
    def sort(self, key = None):
        if key is None:
            key = self._keys[0]
        sortInds = np.stack(self.stored[key]).argsort()
        for k, v in self.zipstacked:
            self.stored[k][:] = v[sortInds]
    def clear(self, silent = False):
        if not silent:
            if not len(self.hashVals):
                raise OutsAlreadyCleared
        self.hashVals.clear()
        for k, v in self.stored.items():
            v.clear()
        self.n = 0
    def retrieve(self, index):
        for v in self.stored.values():
            yield v[index]
    def pop(self, index):
        _ = self.hashVals.pop(index)
        for v in self.stored.values():
            yield v.pop(index)
    def drop(self, indices):
        keep = [i for i in range(self.n) if not i in indices]
        self.hashVals[:] = [self.hashVals[i] for i in keep]
        for v in self.stored.values():
            v[:] = [v[i] for i in keep]
    def index(self, **kwargs):
        search = lambda k, v: self.stored[k].index(v)
        indices = [search(k, v) for k, v in sorted(kwargs.items())]
        if len(set(indices)) != 1:
            raise ValueError
        return indices[0]
    def keys(self):
        return self.data.keys()
    @property
    def stacked(self):
        if self.n:
            for v in self.stored.values():
                yield np.stack(v)
        else:
            for v in self.stored:
                yield []
    @property
    def zipstacked(self):
        return zip(self._keys, self.stacked)
    @property
    def nbytes(self):
        nbytes = np.array(self.hashVals).nbytes
        for v in self.stored.values():
            nbytes += np.array(v).nbytes
        return nbytes
    @property
    def strnbytes(self):
        return prettify_nbytes(self.nbytes)

def _producer_load_wrapper(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        loaded = func(self, *args, **kwargs)
        leftovers = self._load_process(loaded)
        if len(leftovers):
            raise ProducerLoadFail(leftovers)
    return wrapper
maxToken, minToken = int(1e10) - 1, int(1e9)
makeToken = lambda: random.randint(minToken, maxToken)
def _producer_update_outs(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        toReturn = func(self, *args, **kwargs)
        self._tokens[self.outputSubKey] = makeToken()
        return toReturn
    return wrapper

class Producer(Promptable):

    def __init__(self,
            baselines = dict(),
            **kwargs
            ):

        self.baselines = dict()
        for key, val in sorted(baselines.items()):
            self.baselines[key] = EverestArray(val, extendable = False)

        self._outs = OrderedDict()
        self._tokens = dict()

        super().__init__(baselines = self.baselines, **kwargs)

        # Promptable attributes:
        self._prompt_fns.append(self._producer_prompt)

    @property
    def outputMasterKey(self):
        return '/'.join([k for k in self._outputMasterKey() if len(k)])
    def _outputMasterKey(self):
        yield 'outputs'
    @property
    def outputSubKey(self):
        return '/'.join([k for k in self._outputSubKey() if len(k)])
    def _outputSubKey(self):
        yield ''
    @property
    def outputKey(self):
        keys = [self.outputMasterKey, self.outputSubKey]
        return '/'.join([k for k in keys if len(k)])

    @property
    def outs(self):
        sk = self.outputSubKey
        try:
            outs, token = self._outs[sk], self._tokens[sk]
            if not outs.token == token:
                outsDict = self._out()
                outs.update(outsDict)
        except KeyError:
            outsDict = self._out()
            outs = Outs(outsDict.keys(), sk)
            self._outs[sk] = outs
            try:
                outs.update(outsDict)
            except NullValueDetected:
                pass
        return outs
    def _out(self):
        return OrderedDict()

    def store(self, silent = False):
        self.outs.store(silent = silent)
    def clear(self, silent = False):
        self.outs.clear(silent = silent)
    @property
    def nbytes(self):
        return sum([o.nbytes for o in self._outs.values()])
    @property
    def strnbytes(self):
        return prettify_nbytes(self.nbytes)

    def _producer_prompt(self, prompter):
        self.store()

    @property
    def readouts(self):
        return self.reader.sub(self.outputKey)
    @property
    def writeouts(self):
        return self.writer.sub(self.outputKey)

    @disk.h5filewrap
    def save(self):
        self._save()
        self.outs.clear()
    def _save(self):
        if not self.outs.n:
            raise ProducerNothingToSave
        self.writeouts.add(self, 'producer')
        for key, val in self.outs.zipstacked:
            wrapped = EverestArray(val, extendable = True)
            self.writeouts.add(wrapped, key)

    def _load_process(self, outs):
        return outs
    @_producer_load_wrapper
    def load_index_stored(self, index):
        return dict(zip(self.outs.keys(), self.outs.retrieve(index)))
    @_producer_load_wrapper
    def load_index_disk(self, index):
        ks = self.outs.keys()
        return dict(zip(ks, (self.readouts[k][index] for k in ks)))
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
        except TypeError:
            raise LoadFail
    def load(self, arg):
        return self._load(arg)
    @_producer_load_wrapper
    def load_raw(self, outs):
        return outs
