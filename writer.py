import os
import h5py
import numpy as np
import pickle
import ast
import inspect

from collections.abc import Mapping
from collections import OrderedDict

from . import disk
from . import mpi
from .globevars import \
    _BUILTTAG_, _CLASSTAG_, _BYTESTAG_, _STRINGTAG_, _EVALTAG_

class ExtendableDataset:
    def __init__(self, arg):
        self.arg = arg
class FixedDataset:
    def __init__(self, arg):
        self.arg = arg
class LinkTo:
    def __init__(self, arg):
        self.arg = arg

WRITERTYPES = set([ExtendableDataset, FixedDataset, LinkTo])

class Writer:

    def __init__(
            self,
            name,
            path,
            ):

        from . import builts as builtsmodule

        self.name = name
        self.path = path
        self.h5filename = disk.get_framePath(name, path)
        self.h5file = None
        mpi.dowrap(os.makedirs)(path, exist_ok = True)

        self.builtsmodule = builtsmodule

    def _process_inp(self, inp):
        global _BUILTTAG_, _CLASSTAG_, _BYTESTAG_, _STRINGTAG_, _EVALTAG_
        if isinstance(inp, Mapping):
            return {
                key: self._process_inp(val) \
                    for key, val in sorted(inp.items())
                }
            raise TypeError
        elif type(inp) is LinkTo:
            inp.arg.anchor(self.name, self.path)
            return inp
        elif type(inp) in {ExtendableDataset, FixedDataset}:
            return inp
        elif type(inp) is str:
            return _STRINGTAG_ + inp
        elif isinstance(inp, self.builtsmodule.Built):
            inp.anchor(self.name, self.path)
            return _BUILTTAG_ + inp.hashID
        elif type(inp) is self.builtsmodule.Meta:
            return _CLASSTAG_ + inp.script
        elif type(inp) in {list, tuple, frozenset}:
            out = list()
            for sub in inp: out.append(self._process_inp(sub))
            assert len(out) == len(inp), "Mismatch in eval lengths!"
            return _EVALTAG_ + str(type(inp)(out))
        else:
            try:
                out = str(inp)
                if not inp == ast.literal_eval(out):
                    raise TypeError
                return _EVALTAG_ + out
            except:
                out = pickle.dumps(inp)
                if not type(inp) == type(pickle.loads(out)):
                    raise TypeError
                return _BYTESTAG_ + str(out)

    def add(self, item, name):
        processed = self._process_inp(item)
        self._add_wrapped(processed, name)

    @disk.h5filewrap
    @mpi.dowrap
    def _add_wrapped(self, item, name):
        self._add(item, name)

    def _add(self, item, name = '/', *names):
        # expects h5filewrap
        if isinstance(item, Mapping):
            for key, val in sorted(item.items()):
                self._add(
                    val,
                    key,
                    *[*names, name],
                    )
        else:
            group = self.h5file.require_group('/' + '/'.join(names))
            if type(item) is LinkTo:
                self._add_link(item.arg.hashID, name, group)
            elif type(item) is ExtendableDataset:
                try: self._extend_dataset(item.arg, name, group)
                except KeyError: self._add_dataset(item.arg, name, group)
            elif type(item) is FixedDataset:
                self._add_dataset(item.arg, name, group)
            else:
                self._add_attr(item, name, group)

    # def _add_ref(self, address, name, group):
    #     group.attrs[name] = self.h5file[address].ref

    # def _add_group(self, item, name, group):
    #     pass

    def _add_link(self, item, name, group):
        if not name in group:
            group[name] = self.h5file[item]

    def _add_attr(self, item, name, group):
        # expects h5filewrap
        group.attrs[name] = item

    def _add_dataset(self, data, name, group):
        # expects h5filewrap
        # shape = [0, *data.shape[1:]]
        maxshape = [None, *data.shape[1:]]
        group.require_dataset(
            name = name,
            data = data,
            shape = data.shape,
            maxshape = maxshape,
            dtype = data.dtype
            )

    def _extend_dataset(self, data, name, group):
        # expects h5filewrap
        dataset = group[name]
        priorlen = dataset.shape[0]
        dataset.resize(priorlen + len(data), axis = 0)
        dataset[priorlen:] = data
