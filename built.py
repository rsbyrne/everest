import numpy as np
import os
import importlib
import h5py
import time
import hashlib
import weakref

from . import frame
from . import utilities
from . import value
from . import disk
from . import mpi
from . import wordhash

from . import _specialnames

BUILTS = dict()
BUFFERSIZE = 2 ** 30

def buffersize_exceeded():
    nbytes = 0
    for builtID, built in sorted(BUILTS.items()):
        try: nbytes += built.nbytes
        except: pass
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
    autosave = False
    saveinterval = 3600. # seconds
    type = 'anon'
    nbytes = 0

    species = genus = family = 'anon'

    def __init__(
            self,
            inputs,
            script,
            meta = {}
            ):

        process_inputs(inputs)

        if hasattr(self, 'out') or hasattr(self, 'iterate'):
            self.count = value.Value(0)
        if hasattr(self, 'out'):
            if not hasattr(self, 'outkeys'):
                raise Exception
            out = self.out
            self.out = lambda: self._out_wrap(
                out
                )
            self.store = self._store
            self.stored = []
            self.dataDict = {}
            self.counts_stored = []
            self.counts_disk = []
            self.counts_captured = []
            self.clear = self._clear
            self.save = self._save
            self.consignments = []
        if hasattr(self, 'iterate'):
            if not hasattr(self, 'load'):
                raise Exception
            if not hasattr(self, 'initialise'):
                raise Exception
            iterate = self.iterate
            self.iterate = lambda n = 1: self._iterate_wrap(
                iterate,
                n,
                self.count
                )
            load = self.load
            self.load = lambda count: self._load_wrap(
                load,
                count
                )
            initialise = self.initialise
            self.initialise = lambda: self._initialise_wrap(
                initialise,
                self.count
                )
            self.reset = self.initialise
            self.initialise()

        script = disk.ToOpen(script)()
        hashID, hashVal = make_hashID(script, inputs, return_hashVal = True)

        stamps = {
            'script': wordhash.get_random_phrase(make_hash(script)),
            'inputs': wordhash.get_random_phrase(make_hash(inputs)),
            'self': hashID
            }

        self.anchored = False
        self.script = script
        self.inputs = inputs
        self.hashVal = hashVal
        self.hashID = hashID
        self.meta = meta
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

    def set_autosave(self, val: bool):
        self.autosave = val
    def set_saveinterval(self, val: float):
        self.saveinterval = val

    def __hash__(self):
        return self.hashVal

    def _check_anchored(self):
        if not self.anchored:
            raise Exception(
                "Must be anchored first."
                )

    def _load_wrap(self, load, count):
        if not self.count() == count:
            loadDict = self._load_dataDict(count)
            load(loadDict)
            self.count.value = count

    def _load_dataDict(self, count):
        if count in self.counts_stored:
            return self._load_dataDict_stored(count)
        else:
            return self._load_dataDict_saved(count)

    def _load_dataDict_stored(self, count):
        storedDict = {
            count: data for count, data in self.stored
            }
        loadData = storedDict[count]
        loadDict = {
            outkey: data \
                for outkey, data in zip(
                    self.outkeys,
                    loadData
                    )
            }
        return loadDict

    @disk.h5filewrap
    def _load_dataDict_saved(self, count):
        self._check_anchored()
        # self.save()
        loadDict = {}
        counts = self.h5file[self.hashID]['outs'][_specialnames.COUNTS_FLAG]
        iterNo = 0
        while True:
            if iterNo >= len(counts):
                raise Exception("Count not found!")
            if counts[iterNo] == count:
                break
            iterNo += 1
        loadDict = {}
        for key in self.outkeys:
            loadData = self.h5file[self.hashID]['outs'][key][iterNo]
            loadDict[key] = loadData
        return loadDict

    def _iterate_wrap(self, iterate, n, count):
        for i in range(n):
            count.value += 1
            iterate()
            if any(self.consignments):
                self.store()

    def _store(self):
        vals = self.out()
        count = self.count()
        if not count in self.counts_captured:
            entry = [count, vals]
            self.stored.append(entry)
            self.stored.sort()
        self._update_counts()
        self.nbytes = self.get_stored_nbytes()
        if self.autosave:
            self._autosave()

    def get_stored_nbytes(self):
        nbytes = 0
        for count in self.stored:
            for data in count[1]:
                nbytes += np.array(data).nbytes
        return nbytes

    def _clear(self):
        self.stored = []
        self.counts_stored = []

    def _update_dataDict(self):
        counts, outs = zip(*self.stored)
        self.dataDict.update({
            key: np.array(val, dtype = self._obtain_dtype(val[0])) \
                for key, val in zip(self.outkeys, zip(*outs))
            })
        self.dataDict[_specialnames.COUNTS_FLAG] = np.array(counts, dtype = 'i8')

    @staticmethod
    def _obtain_dtype(object):
        if type(object) == np.ndarray:
            dtype = object.dtype
        else:
            dtype = type(object)
        return dtype

    def _save(self):
        self._check_anchored()
        if len(self.stored) == 0:
            return None
        self._update_dataDict()
        for key in [_specialnames.COUNTS_FLAG, *self.outkeys]:
            self._add_dataset(
                self.dataDict[key],
                key,
                ['outs',]
                )
        self.clear()
        self._update_counts()
        self.lastsaved = time.time()

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
                if self.anchored:
                    self.save()

    def _initialise_wrap(self, initialise, count):
        count.value = 0
        initialise()

    def _out_wrap(self, out):
        return out()

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

    def _update_counts(self):
        if self.anchored:
            self.counts_disk = self._get_disk_counts()
        self.counts_stored = utilities.unique_list(
            [index for index, data in self.stored]
            )
        self.counts_captured = utilities.unique_list(
            [*self.counts_stored, *self.counts_disk]
            )

    @disk.h5filewrap
    def _get_disk_counts(self):
        counts_disk = []
        selfgroup = self.h5file[self.hashID]
        if 'outs' in selfgroup:
            outsgroup = selfgroup['outs']
            if _specialnames.COUNTS_FLAG in outsgroup:
                counts = outsgroup[_specialnames.COUNTS_FLAG]
                counts_disk.extend(utilities.unique_list(list(counts[...])))
        return counts_disk

    def file(self):
        return h5py.File(self.h5filename)
