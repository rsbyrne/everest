import os
import h5py

from . import disk
from . import mpi

class Writer:

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.h5filename = disk.get_framePath(name, path)
        self.h5file = None
        if mpi.rank == 0:
            os.makedirs(path, exist_ok = True)
        from .builts import Built
        self.BuiltClass = Built

    def add(self, item, *names):
        self._add_item(item, *names)

    @disk.h5filewrap
    def get(self, *names):
        self._get_h5obj(self, names)

    def _add_item(self, item, *names):
        # if not self._check_item(name, groupNames):
        if type(item) is dict:
            subgroupNames = self._add_subgroup(*names)
            for subname, subitem in sorted(item.items()):
                self._add_item(subitem, subname, *subgroupNames)
        elif isinstance(item, self.BuiltClass):
            if not self._check_item(item.hashID):
                item.anchor(self.name, self.path)
            # self._add_link(item.hashID, name, groupNames)
            self._add_ref(item.hashID, *names)
        else:
            self._add_attr(item, *names)

    def _get_h5obj(self, *names):
        # assumes h5file is open
        myobj = self.h5file
        for name in names:
            if name == 'attrs':
                myobj = myobj.attrs
            myobj = myobj[name]
        return myobj

    @disk.h5filewrap
    def _add_subgroup(self, name, *groupNames):
        group = self._get_h5obj(*groupNames)
        if group is None:
            group = self.h5file
        if name in group:
            subgroup = group[name]
        else:
            subgroup = group.create_group(name)
        return [*groupNames, name]

    @disk.h5filewrap
    def _add_attr(self, item, name, *groupNames):
        group = self._get_h5obj(*groupNames)
        group.attrs[name] = item

    @disk.h5filewrap
    def _add_ref(self, address, name, *groupNames):
        group = self._get_h5obj(*groupNames)
        ref = self.h5file[address].ref
        group.attrs[name] = ref

    @disk.h5filewrap
    def _add_dataset(self, data, key, *groupNames):
        group = self.h5file['/'.join(groupNames)]
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
    def _add_link(self, item, name, *groupNames):
        group = self._get_h5obj(*groupNames)
        group[name] = self.h5file[item]

    @disk.h5filewrap
    def _check_item(self, name, *groupNames):
        group = self._get_h5obj(*groupNames)
        return name in group

    def file(self):
        if not mpi.size == 1:
            raise mpi.MPIError
        return h5py.File(self.h5filename)

    #
    #
    #
    #
    # def _get_h5obj(self, names = []):
    #     # assumes h5file is open
    #     myobj = self.h5file
    #     for name in names:
    #         myobj = myobj[name]
    #     return myobj
    #
    # @disk.h5filewrap
    # def _add_subgroup(self, name, groupNames = []):
    #     group = self._get_h5obj(groupNames)
    #     if group is None:
    #         group = self.h5file
    #     if name in group:
    #         subgroup = group[name]
    #     else:
    #         subgroup = group.create_group(name)
    #     return [*groupNames, name]
    #
    # @disk.h5filewrap
    # def _add_attr(self, item, name, groupNames = []):
    #     group = self._get_h5obj(groupNames)
    #     group.attrs[name] = item
    #
    # @disk.h5filewrap
    # def _add_ref(self, address, name, groupNames = []):
    #     group = self._get_h5obj(groupNames)
    #     ref = self.h5file[address].ref
    #     group.attrs[name] = ref
    #
    # @disk.h5filewrap
    # def _add_dataset(self, data, key, groupNames = []):
    #     group = self.h5file['/'.join(groupNames)]
    #     if key in group:
    #         dataset = group[key]
    #     else:
    #         maxshape = [None, *data.shape[1:]]
    #         dataset = group.create_dataset(
    #             name = key,
    #             shape = [0, *data.shape[1:]],
    #             maxshape = maxshape,
    #             dtype = data.dtype
    #             )
    #     priorlen = dataset.shape[0]
    #     dataset.resize(priorlen + len(data), axis = 0)
    #     dataset[priorlen:] = data
    #
    # @disk.h5filewrap
    # def _add_link(self, item, name, groupNames = []):
    #     group = self._get_h5obj(groupNames)
    #     group[name] = self.h5file[item]
    #
    # @disk.h5filewrap
    # def _check_item(self, name, groupNames = []):
    #     group = self._get_h5obj(groupNames)
    #     return name in group
    #
    # def _add_item(self, item, name, groupNames = []):
    #     # if not self._check_item(name, groupNames):
    #     if type(item) is dict:
    #         subgroupNames = self._add_subgroup(name, groupNames)
    #         for subname, subitem in sorted(item.items()):
    #             self._add_item(subitem, subname, subgroupNames)
    #     elif isinstance(item, Built):
    #         if not self._check_item(item.hashID):
    #             item.anchor(self.frameID, self.path)
    #         # self._add_link(item.hashID, name, groupNames)
    #         self._add_ref(item.hashID, name, groupNames)
    #     else:
    #         self._add_attr(item, name, groupNames)
