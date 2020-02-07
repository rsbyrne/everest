import os
import h5py
import numpy as np
import pickle
import ast

from collections.abc import Mapping
from collections import OrderedDict

from . import disk
from . import mpi
from .globevars import _BUILTTAG_, _CLASSTAG_, _BYTESTAG_

class ExtendableDataset:
    def __init__(self, arg):
        self.arg = arg
class FixedDataset:
    def __init__(self, arg):
        self.arg = arg

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

    def _process_built(self, inp):
        global _BUILTTAG_
        return _BUILTTAG_ + inp.hashID

    def _process_builtClass(self, inp):
        global _CLASSTAG_
        return _CLASSTAG_ + inp.hashID

    def _process_bytes(self, inp):
        global _BYTESTAG_
        return _BYTESTAG_ + str(inp)

    def _process_inp(self, inp):
        if isinstance(inp, Mapping):
            raise TypeError
        elif type(inp) is str:
            out = inp
        elif isinstance(inp, self.builtsmodule.Built):
            inp.anchor(self.name, self.path)
            global _BUILTTAG_
            out = _BUILTTAG_ + inp.hashID
        elif type(inp) is self.builtsmodule.Meta:
            global _CLASSTAG_
            out = _CLASSTAG_ + str(inp.typeHash)
        elif type(inp) in {list, tuple, frozenset}:
            out = list()
            for sub in inp: out.append(self._process_inp(sub))
            assert len(out) == len(inp), (inp, out)
            out = str(type(inp)(out))
        else:
            try:
                out = str(inp)
                if not inp == ast.literal_eval(out):
                    raise TypeError
            except:
                out = pickle.dumps(inp)
                if not type(inp) == type(pickle.loads(out)):
                    raise TypeError
                global _BYTESTAG_
                out = _BYTESTAG_ + str(out)
        return out

    def add(self, item, name = '/', *names):
        if isinstance(item, Mapping):
            for key, val in sorted(item.items()):
                self.add(
                    val,
                    key,
                    *[*names, name]
                    )
        else:
            if isinstance(item, ExtendableDataset):
                try: self._extend_dataset(item.arg, name, *names)
                except KeyError: self._add_dataset(item.arg, name, *names)
            elif isinstance(item, FixedDataset):
                self._add_dataset(item.arg, name, *names)
            else:
                item = self._process_inp(item)
                self._add_attr(item, name, *names)

    def _addwrap(func):
        @disk.h5filewrap
        def wrapper(self, item, name, *names):
            group = self.h5file.require_group('/' + '/'.join(names))
            func(self, item, name, group)
        return wrapper

    @_addwrap
    def _add_link(self, item, name, group):
        group[name] = self.h5file[item]

    @_addwrap
    def _add_ref(self, address, name, group):
        group.attrs[name] = self.h5file[address].ref

    @_addwrap
    def _add_attr(self, item, name, group):
        group.attrs[name] = item

    @_addwrap
    def _add_dataset(self, data, name, group):
        # shape = [0, *data.shape[1:]]
        maxshape = [None, *data.shape[1:]]
        group.require_dataset(
            name = name,
            data = data,
            shape = data.shape,
            maxshape = maxshape,
            dtype = data.dtype
            )

    @_addwrap
    def _extend_dataset(self, data, name, group):
        dataset = group[name]
        priorlen = dataset.shape[0]
        dataset.resize(priorlen + len(data), axis = 0)
        dataset[priorlen:] = data
