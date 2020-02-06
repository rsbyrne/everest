import os
import h5py
import numpy as np

from . import disk
from . import mpi
from .globevars import _BUILTTAG_, _CLASSTAG_

class Writer:

    def __init__(
            self,
            name,
            path,
            ):
        self.name = name
        self.path = path
        self.h5filename = disk.get_framePath(name, path)
        self.h5file = None
        mpi.dowrap(os.makedirs)(path, exist_ok = True)
        from . import builts as builtsmodule
        self.builtsmodule = builtsmodule

    def add(self, item, name = '/', *names, _toInitialise = False):
        if type(item) is dict:
            for key, val in sorted(item.items()):
                self.add(
                    val,
                    key,
                    *[*names, name],
                    _toInitialise = _toInitialise
                    )
        else:
            if isinstance(item, self.builtsmodule.Built):
                item.anchor(self.name, self.path)
                self._add_attr(_BUILTTAG_ + item.hashID, name, *names)
            elif type(item) is self.builtsmodule.Meta:
                self._add_attr(_CLASSTAG_ + str(item.typeHash), name, *names)
            elif type(item) is np.ndarray:
                if _toInitialise:
                    self._add_dataset(item, name, *names)
                else:
                    self._extend_dataset(item, name, *names)
            else:
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
        group.attrs[name] = str(item)

    @_addwrap
    def _add_dataset(self, sampleData, name, group):
        if not name in group:
            shape = [0, *sampleData.shape[1:]]
            maxshape = [None, *sampleData.shape[1:]]
            dtype = sampleData.dtype
            group.require_dataset(name, shape, dtype, maxshape = maxshape)

    @_addwrap
    def _extend_dataset(self, data, name, group):
        dataset = group[name]
        priorlen = dataset.shape[0]
        dataset.resize(priorlen + len(data), axis = 0)
        dataset[priorlen:] = data
