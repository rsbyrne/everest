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

from ..exceptions import EverestException
class NoPreBuiltError(EverestException):
    '''That hashID does not correspond to a previously created Built.'''
    pass
class NotOnDiskError(EverestException):
    '''That hashID could not be found at the provided location.'''
    pass

def load(hashID, name, path = '.'):
    try:
        hashID = disk.get_from_h5(name, path, hashID)
    except KeyError:
        raise NotOnDiskError
    typeHash = disk.get_from_h5(name, path, hashID, 'attrs', 'typeHash')
    script = disk.get_from_h5(name, path, '_globals_', '_classes_', 'attrs', str(typeHash))
    imported = disk.local_import_from_str(script)
    inputs = disk.get_from_h5(name, path, hashID, 'inputs', 'attrs')
    obj = imported.build(**inputs)
    obj.anchor(name, path)
    return obj

def get(cls, inputs = dict(), name = 'test', path = '.'):
    inputs, inputsHash, instanceHash, hashID = _get_info(cls, inputs)
    try:
        return _get_prebuilt(hashID)
    except NoPreBuiltError:
        try:
            return load(hashID, name, path)
        except NotOnDiskError:
            return cls(**inputs)

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

class Meta(type):
    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        outCls.script = disk.ToOpen(outCls.__init__.__globals__['__file__'])()
        outCls.typeHash = make_hash(outCls.script)
        return outCls
    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        obj.__init__(**obj.inputs)
        return obj

class Built(metaclass = Meta):

    @staticmethod
    def _deep_process_inputs(inputs):
        for key, val in inputs.items():
            if type(val) is str:
                if val[:len('_path_')] == '_path_':
                    fullPath = val[len('_path_'):]
                    hashID = os.path.basename(fullPath)
                    try:
                        obj = _get_prebuilt(hashID)
                    except NoPreBuiltError:
                        framePath = os.path.dirname(fullPath)
                        splitPath = framePath.split('/')
                        frameName = os.path.splitext(splitPath[-1])[0]
                        outputPath = os.path.join(splitPath[:-1])
                        obj = load(hashID, frameName, outputPath)
                    inputs[key] = obj
    @staticmethod
    def _process_inputs(inputs):
        # designed to be overridden
        pass

    @classmethod
    def build(cls, **kwargs):
        obj = cls.__new__(cls, **kwargs)
        try:
            obj = _get_prebuilt(obj.hashID)
        except NoPreBuiltError:
            obj.__init__(**obj.inputs)
            cls._add_weakref(obj)
        return obj

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
            'inputs': self.inputs,
            'outs': {}
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

    def anchor(self, frameID, path = ''):
        if mpi.rank == 0:
            os.makedirs(path, exist_ok = True)
        self.frameID = frameID
        self.path = path
        self.h5filename = os.path.join(os.path.abspath(path), frameID + '.frm')
        self._add_item(self.localObjects, self.hashID)
        self._add_item(self.globalObjects, '_globals_')
        self.anchored = True
        if hasattr(self, 'count'):
            self._update_counts()
        self._post_anchor_hook()

    def _get_h5obj(self, names = []):
        # assumes h5file is open
        myobj = self.h5file
        for name in names:
            myobj = myobj[name]
        return myobj

    @disk.h5filewrap
    def _add_subgroup(self, name, groupNames = []):
        group = self._get_h5obj(groupNames)
        if group is None:
            group = self.h5file
        if name in group:
            subgroup = group[name]
        else:
            subgroup = group.create_group(name)
        return [*groupNames, name]

    @disk.h5filewrap
    def _add_attr(self, item, name, groupNames = []):
        group = self._get_h5obj(groupNames)
        group.attrs[name] = item

    @disk.h5filewrap
    def _add_ref(self, address, name, groupNames = []):
        group = self._get_h5obj(groupNames)
        ref = self.h5file[address].ref
        group.attrs[name] = ref

    @disk.h5filewrap
    def _add_dataset(self, data, key, groupNames = []):
        group = self.h5file['/'.join(groupNames)]
        if key in group:
            dataset = group[key]
        else:
            maxshape = [None, *data.shape[1:]]
            dataset = group.create_dataset(
                name = key,
                shape = [0, *data.shape[1:]],
                maxshape = maxshape,
                dtype = data.dtype
                )
        priorlen = dataset.shape[0]
        dataset.resize(priorlen + len(data), axis = 0)
        dataset[priorlen:] = data

    @disk.h5filewrap
    def _add_link(self, item, name, groupNames = []):
        group = self._get_h5obj(groupNames)
        group[name] = self.h5file[item]

    @disk.h5filewrap
    def _check_item(self, name, groupNames = []):
        group = self._get_h5obj(groupNames)
        return name in group

    def _add_item(self, item, name, groupNames = []):
        # if not self._check_item(name, groupNames):
        if type(item) is dict:
            subgroupNames = self._add_subgroup(name, groupNames)
            for subname, subitem in sorted(item.items()):
                self._add_item(subitem, subname, subgroupNames)
        elif isinstance(item, Built):
            if not self._check_item(item.hashID):
                item.anchor(self.frameID, self.path)
            # self._add_link(item.hashID, name, groupNames)
            self._add_ref(item.hashID, name, groupNames)
        else:
            self._add_attr(item, name, groupNames)

    def _coanchored(self, coBuilt):
        if hasattr(self, 'h5filename') and hasattr(coBuilt, 'h5filename'):
            return self.h5filename == coBuilt.h5filename
        else:
            return False

    def coanchor(self, coBuilt):
        if not coBuilt.anchored:
            raise Exception("Trying to coanchor to unanchored built!")
        if not self._coanchored(coBuilt):
            self.anchor(coBuilt.frameID, coBuilt.path)

    def _post_anchor_hook(self):
        pass

    def file(self):
        return h5py.File(self.h5filename)
