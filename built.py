import numpy as np
import h5py

from . import utilities
from . import value
from . import disk

def load_built_from_h5(h5file, hashID):
    built_group = h5file[hashID]
    script = built_group.attrs['script'].decode()
    inputs = eval(built_group.attrs['inputs'].decode())
    with disk.TempFile(
                script,
                extension = 'py'
                ) \
            as tempfile:
        imported = disk.local_import(tempfile)
        loaded_built = imported.build(**inputs)
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
    for key, val in inputs.items():
        if type(val) == tuple:
            inputs[key] = list(val)
        if not isinstance(val, Built):
            if not type(val) in _accepted_inputTypes:
                raise Exception(
                    "Type " + str(type(val)) + " not accepted."
                    )
        if isinstance(val, Built):
            subBuilts[key] = val
            inputs[key] = val.hashID

    return subBuilts

class Built:

    def __init__(
            self,
            inputs,
            filepath,
            update = None,
            iterate = None,
            out = None,
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
            self.store = self._store
            self.stored = []
            self.clear = self._clear
        if not initialise is None:
            self.initialise = lambda: self._initialise_wrap(
                initialise,
                count
                )
            self.reset = self.initialise

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
        self.stored.append(
            (self.count(), self.out())
            )

    def _clear(self):
        self.stored = []

    # def _save(self):
    #     if not hasattr(self, path):
    #         raise Exception("Cannot save: not anchored yet.")
    #     if mpi.rank == 0:
    #         with h5py.File(path) as h5file:
    #             selfgroup = h5file[self.hashID]
    #

    def _initialise_wrap(self, initialise, count):
        count.value = 0
        initialise()
        self.update()

    def anchor(self, path):
        self.path = path
        if mpi.rank == 0:
            with h5py.File(path) as h5file:
                selfgroup = h5file[self.hashID]
                selfgroup.attrs['script'] = self.script.encode()
                selfgroup.attrs['inputs'] = str(self.inputs).encode()
        for subBuilt in self.subBuilts:
            subBuilt.anchor(path)

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
