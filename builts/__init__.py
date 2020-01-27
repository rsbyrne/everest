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
class BuiltNotCreatedYet(EverestException):
    '''That hashID does not correspond to a previously created Built.'''
    pass

def _process_subBuilts(inputs, place):
    mpi.message("Processing subbuilts...")
    for key, val in inputs.items():
        if type(val) is str:
            if val[:len('_REF_:')] == '_REF_:':
                properName = val[len('_REF_:'):]
                inputs[key] = load(properName, *place[1:])
    mpi.message("Subbuilts processed.")

def _get_constructorID(hashID, name, path = '.'):
    constructorID = None
    if mpi.rank == 0:
        with h5py.File(os.path.join(path, name) + '.frm') as h5file:
            if 'constructor' in h5file[hashID].attrs.keys():
                constructorID = h5file[h5file[hashID].attrs['constructor']].name
    constructorID = mpi.share(constructorID)
    return constructorID

def load(hashID, name, path = '.'):
    mpi.message("Loading", hashID)
    place = (hashID, name, path)
    constructorID = _get_constructorID(*place)
    if constructorID is None:
        constructor = Constructor
    else:
        constructor = load(constructorID, name, path)
    inputs = disk.get_from_h5(*[*place, 'inputs', 'attrs'])
    _process_subBuilts(inputs, place)
    loadedBuilt = constructor(**inputs)
    mpi.message("Loaded", loadedBuilt.hashID)
    return loadedBuilt

def make_hash(obj):
    if isinstance(obj, Built):
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

BUFFERSIZE = 2 ** 30

def buffersize_exceeded():
    nbytes = 0
    for builtID, builtRef in sorted(Built._prebuilts.items()):
        built = builtRef()
        if not built is None:
            nbytes += built.nbytes
    return nbytes > BUFFERSIZE

class MetaBuilt(type):
    def __call__(cls, **inputs):
        defaultInps = utilities.get_default_kwargs(cls.__init__)
        inputs = {**defaultInps, **inputs}
        if cls is Constructor:
            mpi.message("Calling to instantiate new constructor...")
            cls.typeHash = 0
            obj = cls.__new__(cls, inputs)
            mpi.message("New constructor instantiated.")
        else:
            mpi.message("Calling to create new built from constructor...")
            constructor = Constructor(script = cls)
            obj = constructor(**inputs)
            mpi.message("New built constructed from constructor.")
        return obj

class Built(metaclass = MetaBuilt):

    _prebuilts = dict()

    @classmethod
    def _get_prebuilt(cls, hashID):
        mpi.message("Getting prebuilt...")
        if not type(hashID) is str:
            raise TypeError(hashID, "is not type 'str'")
        try:
            gotbuilt = cls._prebuilts[hashID]()
        except KeyError:
            raise BuiltNotCreatedYet
        if isinstance(gotbuilt, Built):
            mpi.message("Prebuilt got.")
            return gotbuilt
        else:
            del cls._prebuilts[hashID]
            mpi.message("Failed to get prebuilt.")
            raise BuiltNotCreatedYet

    @staticmethod
    def _process_inputs(inputs):
        pass

    def __new__(cls, inputs):
        mpi.message("Creating new Built instance...")
        cls._process_inputs(inputs)
        inputsHash = make_hash(inputs)
        instanceHash = make_hash((cls.typeHash, inputsHash))
        hashID = wordhash.get_random_phrase(instanceHash)
        try:
            mpi.message("Trying to get prebuilt...")
            obj = cls._get_prebuilt(hashID)
            mpi.message("Successfully got prebuilt.")
        except BuiltNotCreatedYet:
            mpi.message("Making new Built instance...")
            obj = super().__new__(cls)
            obj.inputs = inputs
            obj.inputsHash = inputsHash
            obj.instanceHash = instanceHash
            obj.hashID = hashID
            mpi.message("Made new Built instance.")
            mpi.message("Initialising...")
            obj.__init__(**inputs)
            mpi.message("Initialised.")
        mpi.message("Created new Built instance", hashID, ".")
        return obj

    def __init__(self, **kwargs):

        mpi.message("Initialising Built of type", type(self), '...')

        self.nbytes = 0

        self.anchored = False

        self.organisation = kwargs
        self.organisation.update({
            'typeHash': str(self.typeHash),
            'inputsHash': str(self.inputsHash),
            'instanceHash': str(self.instanceHash),
            'hashID': self.hashID,
            'inputs': self.inputs,
            'outs': {}
            })
        if hasattr(self, 'constructor'):
            self.organisation['constructor'] = self.constructor

        self._add_weakref()

        mpi.message("Initialised Built of type ", type(self), 'hashID ', self.hashID, '.')

    def _add_weakref(self):
        self.ref = weakref.ref(self)
        self._prebuilts[self.hashID] = self.ref

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
        self._add_item(self.organisation, self.hashID)
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
        group = self.h5file[self.hashID]['/'.join(groupNames)]
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
        if not self._check_item(name, groupNames):
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

from .constructor import Constructor
