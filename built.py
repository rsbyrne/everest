import numpy as np
import os
import importlib
import h5py
import time

from . import frame
from . import utilities
from . import value
from . import disk
from . import mpi

from . import _specialnames
_specialnames.BUILT_FLAG = '_built_:'
_specialnames.COUNTS_FLAG = '_counts_'
_specialnames.SCRIPT_FLAG = '_script_'

# INPUTS_FLAG = '_inputs_'

def load(name, hashID, path = ''):
    framepath = frame.get_framepath(name, path)
    attrs = disk.h5_read_attrs(framepath, subkeys = [hashID,])
    def _load_process_input(val):
        if not type(val) is str:
            val = eval(str(val))
        elif val[:len(_specialnames.BUILT_FLAG)] == _specialnames.BUILT_FLAG:
            loadHashID = val[len(_specialnames.BUILT_FLAG):]
            val = load(name, loadHashID, path)
        return val
    inputs = {
        key: _load_process_input(val) \
            for key, val in sorted(attrs.items())
        }
    script = inputs.pop(_specialnames.SCRIPT_FLAG)
    with disk.TempFile(
                script,
                extension = 'py',
                mode = 'wb'
                ) \
            as tempfile:
        imported = disk.local_import(tempfile)
        loadedBuilt = imported.build(**inputs)
    loadedBuilt.anchor(name, path)
    return loadedBuilt

def _clean_inputs(inputs):

    # _accepted_inputTypes = {
    #     type([]),
    #     type(0),
    #     type(0.),
    #     type('0'),
    #     }

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
        if not isinstance(val, Built):
            if not type(val) is str:
                val = eval(str(val))
        # if type(val) == tuple:
        #     inputs[key] = list(val)
        # if not isinstance(val, Built):
        #     if not type(val) in _accepted_inputTypes:
        #         raise Exception(
        #             "Type " + str(type(val)) + " not accepted."
        #             )
        if isinstance(val, Built):
            subBuilts[key] = val
            safeInputs[key] = _specialnames.BUILT_FLAG + val.hashID
        else:
            safeInputs[key] = inputs[key]

    return inputs, safeInputs, subBuilts

class Built:

    def __init__(
            self,
            inputs,
            script,
            meta = {}
            ):

        if hasattr(self, 'update'):
            update = self.update
            self.update = lambda: self._update_wrap(update)
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

        inputs, safeInputs, subBuilts = _clean_inputs(inputs)

        script = utilities.ToOpen(script)()
        hashID = utilities.wordhashstamp(
            (script, sorted(safeInputs.items()))
            )

        self.anchored = False
        self.script = script
        self.inputs = inputs
        self.safeInputs = safeInputs
        self.subBuilts = subBuilts
        self.hashID = hashID
        self.meta = meta

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

    def _load_dataDict_saved(self, count):
        self._check_anchored()
        self.save()
        loadDict = {}
        if mpi.rank == 0:
            with disk.h5File(self.fullpath) as h5file:
                selfgroup = h5file[self.hashID]
                counts = selfgroup[_specialnames.COUNTS_FLAG]
                iterNo = 0
                while True:
                    if iterNo >= len(counts):
                        raise Exception("Count not found!")
                    if counts[iterNo] == count:
                        break
                    iterNo += 1
                loadDict = {}
                for key in self.outkeys:
                    loadData = selfgroup[key][iterNo]
                    loadDict[key] = loadData
        loadDict = mpi.comm.bcast(loadDict, root = 0)
        return loadDict

    def _iterate_wrap(self, iterate, n, count):
        for i in range(n):
            count.value += 1
            iterate()

    def _update_wrap(self, update):
        update()

    def go(self, n):
        for i in range(n):
            self.iterate()

    def _store(self):
        self.update()
        vals = self.out()
        count = self.count()
        if not count in self.counts_captured:
            entry = [count, vals]
            self.stored.append(entry)
            self.stored.sort()
        self._update_counts()

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
            self._extend_dataSet(key)
        self.clear()

    def _extend_dataSet(self, key):
        data = self.dataDict[key]
        if mpi.rank == 0:
            with disk.h5File(self.fullpath) as h5file:
                selfgroup = h5file[self.hashID]
                if key in selfgroup:
                    dataset = selfgroup[key]
                else:
                    maxshape = [None, *data.shape[1:]]
                    dataset = selfgroup.create_dataset(
                        name = key,
                        shape = [0, *data.shape[1:]],
                        maxshape = maxshape,
                        dtype = data.dtype
                        )
                priorlen = dataset.shape[0]
                dataset.resize(priorlen + len(data), axis = 0)
                dataset[priorlen:] = data

    def _initialise_wrap(self, initialise, count):
        count.value = 0
        initialise()

    def _out_wrap(self, out):
        return out()

    def anchor(self, frameID = None, path = ''):
        if frameID is None:
            frameID = self.hashID
        fullpath = frame.get_framepath(frameID, path)
        if mpi.rank == 0:
            os.makedirs(path, exist_ok = True)
            with disk.h5File(fullpath) as h5file:
                if self.hashID in h5file:
                    selfgroup = h5file[self.hashID]
                else:
                    selfgroup = h5file.create_group(self.hashID)
                attrs = {
                    _specialnames.SCRIPT_FLAG: bytes(self.script.encode()),
                    **self.safeInputs,
                    **self.meta
                    }
                for key, val in sorted(attrs.items()):
                    selfgroup.attrs[key] = val
        for key, subBuilt in sorted(self.subBuilts.items()):
            subBuilt.anchor(frameID, path)
        self.frameID = frameID
        self.path = path
        self.fullpath = fullpath
        self.anchored = True
        if hasattr(self, 'count'):
            self._update_counts()
        self._post_anchor_hook()

    def coanchor(self, coBuilt):
        self.anchor(coBuilt.frameID, coBuilt.path)

    def _post_anchor_hook(self):
        pass

    def _update_counts(self):
        if self.anchored:
            if mpi.rank == 0:
                with disk.h5File(self.fullpath) as h5file:
                    selfgroup = h5file[self.hashID]
                    if _specialnames.COUNTS_FLAG in selfgroup:
                        self.counts_disk = utilities.unique_list(
                            list(
                                selfgroup[_specialnames.COUNTS_FLAG][...]
                                )
                            )
            self.counts_disk = mpi.comm.bcast(self.counts_disk, root = 0)
        self.counts_stored = utilities.unique_list(
            [index for index, data in self.stored]
            )
        self.counts_captured = utilities.unique_list(
            [*self.counts_stored, *self.counts_disk]
            )

    def file(self):
        return h5py.File(self.fullpath)
