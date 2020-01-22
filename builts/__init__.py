import numpy as np
import os
import importlib
import h5py
import time
import hashlib
import weakref

from .. import frame
from .. import utilities

from .. import disk
from .. import mpi
from .. import wordhash
from .. import _specialnames

BUILTS = dict()
BUFFERSIZE = 2 ** 30

def buffersize_exceeded():
    nbytes = 0
    for builtID, builtRef in sorted(BUILTS.items()):
        built = builtRef()
        if not built is None:
            nbytes += built.nbytes
    return nbytes > BUFFERSIZE

def buildWrap(func, builtClass):
    def wrapper(_direct = False, **inputs):
        defaultInps = utilities.get_default_args(builtClass)
        inputs = {**defaultInps, **inputs}
        if _direct: return func(**inputs)
        filename = builtClass.__init__.__globals__['__file__']
        script = disk.ToOpen(filename)()
        hashID = make_hashID(script, inputs)
        try:
            built = get(hashID)
        except KeyError:
            built = func(**inputs)
        assert built.hashID == hashID, (built.inputs, inputs)
        return built
        # except KeyError: return construct(script, inputs)
    return wrapper

def make_buildFn(builtClass):
    def build(**kwargs):
        built = builtClass(**kwargs)
        return built
    return buildWrap(build, builtClass)

def construct(script, inputs):
    with disk.TempFile(
                script,
                extension = 'py',
                mode = 'w'
                ) \
            as tempfile:
        imported = disk.local_import(tempfile)
        constructed = imported.build(_direct = True, **inputs)
    return constructed

def get(hashID):
    gotbuilt = BUILTS[hashID]()
    if isinstance(gotbuilt, Built):
        return gotbuilt
    else:
        del BUILTS[hashID]
        raise KeyError

def make_hashID(script, inputs, return_hashVal = False):
    hashVal = make_hash((script, inputs))
    hashID = wordhash.get_random_phrase(hashVal)
    if return_hashVal:
        return hashID, hashVal
    else:
        return hashID

def load(hashID, name, path = ''):
    try:
        loadedBuilt = get(hashID)
    except KeyError:
        loadedBuilt = _load(hashID, name, path)
    loadedBuilt.anchor(name, path)
    return loadedBuilt

def _load(hashID, name, path = ''):
    framepath = frame.get_framepath(name, path)
    script = None
    inputs = {}
    subBuiltIDs = {}
    if mpi.rank == 0:
        h5file = h5py.File(framepath, mode = 'r')
        h5group = h5file[hashID]
        script = h5group.attrs['script']
        inputsGroup = h5group['inputs']
        for key, val in inputsGroup.attrs.items():
            if type(val) is h5py.Reference:
                subBuiltIDs[key] = h5file[val].attrs['hashID']
            else:
                inputs[key] = np.array(val).item()
    inputs = mpi.comm.bcast(inputs, root = 0)
    subBuiltIDs = mpi.comm.bcast(subBuiltIDs, root = 0)
    for key, val in sorted(subBuiltIDs.items()):
        inputs[key] = load(subBuiltIDs[key], name, path)
    loadedBuilt = construct(script, inputs)
    return loadedBuilt

def process_inputs(inputs):
    badKeys = {
        'args',
        'kwargs',
        'self',
        '__class__'
        }
    for key in badKeys:
        if key in inputs:
            del inputs[key]

def make_hash(obj):
    if isinstance(obj, Built):
        hashVal = hash(obj)
    elif type(obj) is str:
        hashVal = hash(int(
            hashlib.md5(obj.encode()).hexdigest(),
            16
            ))
    elif type(obj) is list or type(obj) is tuple:
        hashVal = hash(
            tuple([
                make_hash(subobj) \
                    for subobj in obj
                ])
            )
    elif type(obj) is dict:
        hashVal = hash(
            tuple([
                (make_hash(key), make_hash(val)) \
                    for key, val in sorted(obj.items())
                ])
            )
    elif isinstance(obj, np.generic):
        hashVal = make_hash(np.asscalar(obj))
    else:
        hashVal = make_hash(str(obj))
    return hashVal

class Built:

    h5file = None
    h5filename = None
    type = 'anon'

    species = genus = 'anon'
    inputs = dict()
    script = None
    meta = dict()

    def __init__(self):

        process_inputs(self.inputs)

        script = disk.ToOpen(script)()
        hashID, hashVal = make_hashID(script, inputs, return_hashVal = True)

        stamps = {
            'script': wordhash.get_random_phrase(make_hash(script)),
            'inputs': wordhash.get_random_phrase(make_hash(inputs)),
            'self': hashID
            }

        self.anchored = False
        self.hashVal = hashVal
        self.hashID = hashID
        self.stamps = stamps

        self.organisation = {
            'inputs': inputs,
            'script': script,
            'meta': meta,
            'stamps': stamps,
            'type': self.type,
            'hashID': hashID,
            'outs': {},
            'temp': {}
            }

        self._add_weakref()

    def _add_weakref(self):
        self.ref = weakref.ref(self)
        BUILTS[self.hashID] = self.ref

    def __hash__(self):
        return self.hashVal

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
        self.h5filename = frame.get_framepath(frameID, path)
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
