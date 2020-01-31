import numpy as np
import os
import importlib
import h5py
import time
import hashlib
import weakref

from .. import utilities
from .. import disk
from .. import mpi
from .. import wordhash
from ..writer import Writer
from ..reader import Reader

from ..globevars import _BUILTTAG_, _CLASSTAG_

from ..exceptions import EverestException
class NoPreBuiltError(EverestException):
    '''That hashID does not correspond to a previously created Built.'''
    pass
class NotOnDiskError(EverestException):
    '''That hashID could not be found at the provided location.'''
    pass
class NotInFrameError(EverestException):
    '''No frame by that name could be found.'''
    pass
class BuiltNotFoundError(EverestException):
    '''A Built with those parameters could not be found.'''
    pass
class NoPreClassError(EverestException):
    '''That typeHash is not associated with a class on file yet.'''
    pass

def load(hashID, name, path = '.', get = False):
    try: ignoreMe = Reader(name, path)[hashID]
    except KeyError: raise NotInFrameError
    except OSError: raise NotOnDiskError
    cls = load_class(hashID, name, path)
    inputs = Reader(name, path)[hashID, 'inputs', '*']
    _process_loaded_inputs(inputs, name, path, get = get)
    if get: obj = cls.get(**inputs)
    else: obj = cls.build(**inputs)
    assert obj.hashID == hashID, "Loaded hashID does not match input!"
    obj.anchor(name, path)
    return obj

def _process_loaded_inputs(inputs, name, path, **kwargs):
    for key, val in inputs.items():
        if type(val) is str:
            if val.startswith(_BUILTTAG_):
                inputs[key] = load(val.lstrip(_BUILTTAG_), name, path, **kwargs)
            elif val.startswith(_CLASSTAG_):
                inputs[key] = load_class(val.lstrip(_CLASSTAG_), name, path)

def load_class(hashID, name, path):
    reader = Reader(name, path)
    script = reader['_globals_', '_classes_', reader[hashID, 'typeHash']]
    outclass = disk.local_import_from_str(script).CLASS
    return outclass

def _get_inputs(cls, inputs = dict()):
    defaultInps = utilities.get_default_kwargs(cls.__init__)
    inputs = {**defaultInps, **inputs}
    cls._deep_process_inputs(inputs)
    cls._process_inputs(inputs)
    return inputs

def _get_hashes(cls, inputs):
    inputsHash = make_hash(inputs)
    instanceHash = make_hash((cls.typeHash, inputsHash))
    hashID = wordhash.get_random_phrase(instanceHash)
    return inputsHash, instanceHash, hashID

def _get_info(cls, inputs = dict()):
    inputs = _get_inputs(cls, inputs)
    inputsHash, instanceHash, hashID = _get_hashes(cls, inputs)
    return inputs, inputsHash, instanceHash, hashID

def make_hash(obj):
    if hasattr(obj, 'instanceHash'):
        hashVal = obj.instanceHash
    elif type(obj) is dict:
        hashVal = make_hash(sorted(obj.items()))
    elif type(obj) is list or type(obj) is tuple:
        hashList = [make_hash(subObj) for subObj in obj]
        hashVal = make_hash(str(hashList))
    elif isinstance(obj, np.generic):
        hashVal = make_hash(np.asscalar(obj))
    else:
        strObj = str(obj)
        hexID = hashlib.md5(strObj.encode()).hexdigest()
        hashVal = int(hexID, 16)
    return hashVal

_PREBUILTS = dict()
def _get_prebuilt(hashID):
    if not type(hashID) is str:
        raise TypeError(hashID, "is not type 'str'")
    try:
        gotbuilt = _PREBUILTS[hashID]()
    except KeyError:
        raise NoPreBuiltError
    if isinstance(gotbuilt, Built):
        return gotbuilt
    else:
        del _PREBUILTS[hashID]
        raise NoPreBuiltError

BUFFERSIZE = 2 ** 30
def buffersize_exceeded():
    nbytes = 0
    for builtID, builtRef in sorted(_PREBUILTS.items()):
        built = builtRef()
        if not built is None:
            nbytes += built.nbytes
    return nbytes > BUFFERSIZE

_PRECLASSES = dict()
def _get_preclass(typeHash):
    try:
        outclass = _PRECLASSES[typeHash]
        assert not outclass is None
        return outclass
    except AssertionError:
        del _PRECLASSES[typeHash]
    except KeyError:
        pass
    finally:
        raise NoPreClassError

class Meta(type):
    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        outCls.script = disk.ToOpen(outCls.__init__.__globals__['__file__'])()
        outCls.typeHash = make_hash(outCls.script)
        try:
            return _get_preclass(outCls.typeHash)
        except NoPreClassError:
            _PRECLASSES[outCls.typeHash] = weakref.ref(outCls)
            return outCls
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        obj.__init__(**obj.inputs)
        return obj

class Built(metaclass = Meta):

    @staticmethod
    def _deep_process_inputs(inputs):
        for key, val in inputs.items():
            if type(val) is np.ndarray:
                inputs[key] = list(val)
    @staticmethod
    def _process_inputs(inputs):
        # designed to be overridden
        pass

    @classmethod
    def get(cls, **kwargs):
        obj = cls.__new__(cls, **kwargs)
        try:
            return _get_prebuilt(obj.hashID)
        except NoPreBuiltError:
            obj.__init__(**obj.inputs)
            cls._add_weakref(obj)
        return obj

    @classmethod
    def build(cls, **kwargs):
        return cls(**kwargs)

    @staticmethod
    def _add_weakref(obj):
        if not obj.hashID in _PREBUILTS:
            obj.ref = weakref.ref(obj)
            _PREBUILTS[obj.hashID] = obj.ref

    def __new__(cls, **inputs):
        inputs, inputsHash, instanceHash, hashID = _get_info(cls, inputs)
        obj = super().__new__(cls)
        obj.inputs = inputs
        obj.inputsHash = inputsHash
        obj.instanceHash = instanceHash
        obj.hashID = hashID
        obj._initialised = False
        obj._pre_anchor_fns = []
        obj._post_anchor_fns = []
        return obj

    def __init__(self, **customAttributes):

        self.nbytes = 0

        self.anchored = False

        self.localObjects = dict()
        self.localObjects.update(customAttributes)
        self.localObjects.update({
            'typeHash': str(self.typeHash),
            'inputsHash': str(self.inputsHash),
            'instanceHash': str(self.instanceHash),
            'hashID': self.hashID,
            'inputs': self.inputs
            })
        self.globalObjects = {
            '_classes_': {str(self.typeHash): self.script}
            }

        super().__init__()

    def __hash__(self):
        return self.instanceHash

    def _check_anchored(self):
        if not self.anchored:
            raise Exception(
                "Must be anchored first."
                )

    def anchor(self, name, path = ''):
        for fn in self._pre_anchor_fns: fn()
        self.name, self.path = name, path
        writer = Writer(name, path)
        writer.add(self.localObjects, self.hashID, _toInitialise = True)
        writer.add(self.globalObjects, '_globals_', _toInitialise = True)
        self.anchored = True
        if hasattr(self, 'count'):
            self._update_counts()
        for fn in self._post_anchor_fns: fn()

    def _coanchored(self, coBuilt):
        if hasattr(self, 'h5filename') and hasattr(coBuilt, 'h5filename'):
            return self.writer.h5filename == coBuilt.writer.h5filename
        else:
            return False

    def coanchor(self, coBuilt):
        if not coBuilt.anchored:
            raise Exception("Trying to coanchor to unanchored built!")
        if not self._coanchored(coBuilt):
            self.anchor(coBuilt.frameID, coBuilt.path)
