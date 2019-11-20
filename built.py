import numpy as np
import h5py

from . import utilities
from . import value
from . import disk
from . import mpi

BUILT_FLAG = 'BUILT:'

def load_built_from_h5(path, hashID):
    script = ''
    inputs = ''
    attrs = disk.h5_read_attrs(path, subkeys = [hashID,])
    script = attrs['script']
    inputs = eval(attrs['inputs'])
    for key, val in sorted(inputs.items()):
        if type(val) is str:
            if val[:6] == BUILT_FLAG:
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
            inputs[key] = BUILT_FLAG + val.hashID

    return subBuilts

class Built:

    def __init__(
            self,
            inputs,
            filepath,
            update = None,
            iterate = None,
            out = None,
            outkeys = None,
            initialise = None
            ):

        subBuilts = _clean_inputs(inputs)

        script = utilities.ToOpen(filepath)()
        hashID = utilities.wordhashstamp((script, inputs))

        if not update is None:
            self.update = lambda: self._update_wrap(
                update
                )
        if not iterate is None:
            count = value.Value(0)
            self.iterate = lambda: self._iterate_wrap(
                iterate,
                count
                )
            def go(n):
                for i in range(n):
                    self.iterate()
            self.go = go
            self.count = count
        if not out is None:
            self.out = lambda: self._out_wrap(
                out
                )
            if not iterate is None:
                if outkeys is None:
                    raise Exception(
                        "Must provide outkeys when providing out and iterate."
                        )
                if not len(outkeys) == len(self.out()):
                    raise Exception(
                        "Must provide outkey for each out."
                        )
                self.outkeys = outkeys
                self.store = self._store
                self.stored = []
                self.clear = self._clear
                self.save = self._save
        if not initialise is None:
            self.initialise = lambda: self._initialise_wrap(
                initialise,
                count
                )
            self.reset = self.initialise

        self.anchored = False
        self.script = script
        self.inputs = inputs
        self.subBuilts = subBuilts
        self.hashID = hashID

        if not initialise is None:
            self.initialise()

    def _out_wrap(self, out):
        return out()

    def _update_wrap(self, update):
        update()

    def _iterate_wrap(self, iterate, count):
        count.value += 1
        iterate()
        self.update()

    def _store(self):
        val = self.out()
        count = self.count()
        past_counts = [index for index, data in self.stored]
        if not count in past_counts:
            entry = (count, val)
            self.stored.append(entry)
        self.stored.sort()

    def _clear(self):
        self.stored = []

    def _make_dataDict(self):
        stored = self.stored
        outkeys = self.outkeys
        counts, outs = zip(*stored)
        dataDict = {key: np.array(val) for key, val in zip(outkeys, zip(*outs))}
        dataDict['counts'] = np.array(counts)
        return dataDict

    def _save(self):
        if not self.anchored:
            raise Exception("Cannot save: not anchored yet.")
        dataDict = self._make_dataDict()
        with h5py.File(
                    self.path,
                    driver = 'mpio',
                    comm = mpi.comm
                    ) \
                as h5file:
            selfgroup = h5file[self.hashID]
            for key, data in sorted(dataDict.items()):
                if key in selfgroup:
                    dataset = selfgroup[key]
                else:
                    maxshape = [None, *data.shape[1:]]
                    dataset = selfgroup.create_dataset(
                        name = key,
                        shape = [0, *data.shape[1:]],
                        maxshape = maxshape
                        # compression = 'gzip'
                        )
                priorlen = dataset.shape[0]
                dataset.resize(priorlen + len(data), axis = 0)
                dataset[priorlen:] = data
        self.clear()

    def _initialise_wrap(self, initialise, count):
        count.value = 0
        initialise()
        self.update()

    def anchor(self, path):
        if mpi.rank == 0:
            with h5py.File(path) as h5file:
                if self.hashID in h5file:
                    selfgroup = h5file[self.hashID]
                else:
                    selfgroup = h5file.create_group(self.hashID)
                selfgroup.attrs['script'] = self.script.encode()
                selfgroup.attrs['inputs'] = str(self.inputs).encode()
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

    # def _initialise_wrap(self, initialise, count, inBuiltDict):
    #     count.value = 0
    #     self.initials.update(inBuiltDict)
    #     inHashDict = {
    #         key: inBuilt.hashID \
    #             for key, inBuilt in sorted(self.initials.items())
    #             }
    #     self.initials_hashIDs.update(inHashDict)
    #     self.initials_allHash = utilities.wordhashstamp(
    #         self.initials_hashIDs
    #         )
    #     inDataDict = {
    #         key: inBuilt.out() \
    #             for key, inBuilt in sorted(self.initials.items())
    #             }
    #     initialise(**inDataDict)
