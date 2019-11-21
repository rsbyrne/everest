import numpy as np
import h5py

from . import utilities
from . import value
from . import disk
from . import mpi

BUILT_FLAG = '_built:'
COUNTS_FLAG = '_counts'

def load_built_from_h5(path, hashID):
    script = ''
    inputs = ''
    attrs = disk.h5_read_attrs(path, subkeys = [hashID,])
    script = attrs['script']
    inputs = eval(attrs['inputs'])
    for key, val in sorted(inputs.items()):
        if type(val) is str:
            if val[:len(BUILT_FLAG)] == BUILT_FLAG:
                loadHashID = val[6:]
                loadedBuilt = load_built_from_h5(path, loadHashID)
                inputs[key] = loadedBuilt
    with disk.TempFile(
                script,
                extension = 'py'
                ) \
            as tempfile:
        imported = disk.local_import(tempfile)
        loaded_built = imported.build(**inputs)
    loaded_built.anchor(path)
    return loaded_built

def _clean_inputs(inputs):

    _accepted_inputTypes = {
        type([]),
        type(0),
        type(0.),
        type('0'),
        }

    badKeys = {
        'args',
        'kwargs',
        'self',
        '__class__'
        }
    for key in badKeys:
        if key in inputs:
            del inputs[key]

    subBuilts = {}
    safeInputs = {}
    for key, val in sorted(inputs.items()):
        if type(val) == tuple:
            inputs[key] = list(val)
        if not isinstance(val, Built):
            if not type(val) in _accepted_inputTypes:
                raise Exception(
                    "Type " + str(type(val)) + " not accepted."
                    )
        if isinstance(val, Built):
            subBuilts[key] = val
            safeInputs[key] = BUILT_FLAG + val.hashID

    return inputs, safeInputs, subBuilts

class Built:

    def __init__(
            self,
            inputs,
            filepath,
            # out,
            # outkeys,
            # update,
            # iterate,
            # initialise,
            # load
            ):

        if hasattr(self, 'out'):
            if not hasattr(self, 'outkeys'):
                raise Exception
            out = self.out
            self.out = lambda: self._out_wrap(
                out
                )
        if hasattr(self, 'update'):
            update = self.update
            self.update = lambda: self._update_wrap(
                update
                )
        if hasattr(self, 'iterate'):
            self.count = value.Value(0)
            iterate = self.iterate
            self.iterate = lambda: self._iterate_wrap(
                iterate,
                self.count
                )
            self.store = self._store
            self.stored = []
            self.stored_counts = []
            self.clear = self._clear
            self.save = self._save
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

        inputs, safeInputs, subBuilts = _clean_inputs(inputs)

        script = utilities.ToOpen(filepath)()
        hashID = utilities.wordhashstamp((script, safeInputs))

        self.anchored = False
        self.script = script
        self.inputs = inputs
        self.safeInputs = safeInputs
        self.subBuilts = subBuilts
        self.hashID = hashID

    def _check_anchored(self):
        if not self.anchored:
            raise Exception(
                "Must be anchored first."
                )

    def _load_wrap(self, load, count):
        loadDict = self._load_dataDict(count)
        load(loadDict)
        self.count.value = count

    def _load_dataDict(self, count):
        if count in self.stored_counts:
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

    def _load_dataDict_saved(self, count):
        self._check_anchored()
        self.save()
        with h5py.File(
                    self.path,
                    driver = 'mpio',
                    comm = mpi.comm
                    ) \
                as h5file:
            selfgroup = h5file[self.hashID]
            counts = selfgroup[COUNTS_FLAG]['data']
            iterNo = 0
            while True:
                if iterNo >= len(counts):
                    raise Exception("Count not found!")
                if counts[iterNo] == count:
                    break
                iterNo += 1
            loadDict = {}
            for key in self.outkeys:
                loadData = selfgroup[key]['data'][iterNo]
                loadDict[key] = loadData
        return loadDict

    def _update_wrap(self, update):
        update()

    def _iterate_wrap(self, iterate, count):
        count.value += 1
        iterate()
        self.update()

    def go(self, n):
        for i in range(n):
            self.iterate()

    def _store(self):
        val = self.out()
        count = self.count()
        self.stored_counts = [index for index, data in self.stored]
        if not count in self.stored_counts:
            entry = (count, val)
            self.stored.append(entry)
            self.stored.sort()
            self.stored_counts.append(count)
            self.stored_counts.sort()

    def _clear(self):
        self.stored = []

    def _make_dataDict(self, stored, outkeys):
        counts, outs = zip(*stored)
        dataDict = {
            key: np.array(val, dtype = self._obtain_dtype(val[0])) \
                for key, val in zip(outkeys, zip(*outs))
            }
        dataDict[COUNTS_FLAG] = np.array(counts, dtype = 'i8')
        return dataDict

    @staticmethod
    def _obtain_dtype(object):
        if type(object) == np.ndarray:
            dtype = object.dtype
        else:
            dtype = type(object)
        return dtype

    def _save(self):
        self._check_anchored()
        with h5py.File(
                    self.path,
                    driver = 'mpio',
                    comm = mpi.comm
                    ) \
                as h5file:
            selfgroup = h5file[self.hashID]
            if COUNTS_FLAG in selfgroup:
                saved_counts = list(selfgroup[COUNTS_FLAG]['data'][...])
                purged_stored = []
                for index, (count, values) in enumerate(self.stored):
                    if not count in saved_counts:
                        purged_stored.append(self.stored[index])
                self.stored = purged_stored
            if len(self.stored) > 0:
                dataDict = self._make_dataDict(
                    self.stored,
                    self.outkeys
                    )
                for key in [COUNTS_FLAG, *self.outkeys]:
                    data = dataDict[key]
                    if key in selfgroup:
                        outgroup = selfgroup[key]
                        dataset = outgroup['data']
                    else:
                        outgroup = selfgroup.create_group(key)
                        maxshape = [None, *data.shape[1:]]
                        dataset = outgroup.create_dataset(
                            name = 'data',
                            shape = [0, *data.shape[1:]],
                            maxshape = maxshape,
                            dtype = data.dtype
                            # compression = 'gzip'
                            )
                        if not key == COUNTS_FLAG:
                            outgroup[COUNTS_FLAG] = \
                                selfgroup[COUNTS_FLAG]['data']
                    priorlen = dataset.shape[0]
                    dataset.resize(priorlen + len(data), axis = 0)
                    dataset[priorlen:] = data
        self.clear()

    def _initialise_wrap(self, initialise, count):
        count.value = 0
        initialise()
        self.update()

    def _out_wrap(self, out):
        return out()

    def anchor(self, path):
        if mpi.rank == 0:
            with h5py.File(path) as h5file:
                if self.hashID in h5file:
                    selfgroup = h5file[self.hashID]
                else:
                    selfgroup = h5file.create_group(self.hashID)
                selfgroup.attrs['script'] = self.script.encode()
                selfgroup.attrs['inputs'] = str(self.safeInputs).encode()
        for key, subBuilt in sorted(self.subBuilts.items()):
            subBuilt.anchor(path)
        self.path = path
        self.anchored = True

    def outget(self, key):
        if key in self.subBuilts:
            return self.subBuilts[key].out()
        elif key in self.inputs:
            return self.inputs[key]
        else:
            raise Exception(
                "Key not found in either subBuilts or inputs"
                )
