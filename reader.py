import h5py
from functools import partial
from functools import reduce
import operator
import os
import numpy as np
import ast
import pickle

from . import disk
from . import utilities
from .fetch import Fetch
from .scope import Scope
from .globevars import \
    _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
    _BYTESTAG_, _STRINGTAG_, _EVALTAG_

# class ReadWriteAgent:
#
#     _BUILTTAG_ = '_built_'
#     _CLASSTAG_ = '_class_'
#     _ADDRESSTAG_ = '_address_'
#     _BYTESTAG_ = '_bytes_'
#     _STRINGTAG_ = '_string_'
#     _EVALTAG_ = '_eval_'
#
#     def __init__(self,
#             name,
#             path
#             ):
#         self.name, self.path = name, path
#         from . import builts as builtsModule
#         self.builtsModule = builtsModule
#
#     def process(self, inp, mode):
#         pass
#
#     def _process_str(self, inp, mode):
#         if mode == 'w':
#             return inp
#         elif mode == 'r':
#             return self.process()
#
#     def _process_built(self, inp, mode):


class Reader:

    def __init__(
            self,
            name,
            path
            ):
        self.name, self.path = name, path
        self.h5file = None
        self.h5filename = os.path.join(os.path.abspath(path), name + '.frm')
        self.file = partial(h5py.File, self.h5filename, 'r')
        from . import builts as builtsmodule
        self._builtsModule = builtsmodule

    @disk.h5filewrap
    def pull(self, scope, keys):
        if type(keys) is str:
            keys = (keys,)
        outs = []
        for key in keys:
            outs.append(self._pull(scope, key))
        if len(outs) == 1:
            return outs[0]
        else:
            return tuple(outs)

    def _pull(self, scope, key):
        arrList = []
        for superkey, scopeCounts in scope:
            thisGroup = self.h5file[superkey]
            thisTargetDataset = thisGroup[key]
            if scopeCounts == '...':
                arr = thisTargetDataset[...]
            else:
                thisCountsDataset = thisGroup['outputs']['count']
                maskArr = np.isin(
                    thisCountsDataset,
                    scopeCounts,
                    assume_unique = True
                    )
                slicer = (
                    maskArr,
                    *[slice(None) for i in range(1, len(thisTargetDataset.shape))]
                    )
                arr = thisTargetDataset[slicer]
            arrList.append(arr)
        try:
            allArr = np.concatenate(arrList)
            return allArr
        except ValueError:
            allTuple = tuple(arrList)
            return allTuple

    def _recursive_seek(self, key, searchArea = None):
        # expects h5filewrap
        if searchArea is None:
            searchArea = self.h5file
        splitkey = key.split('/')
        primekey = splitkey[0]
        remkey = '/'.join(splitkey[1:])
        if primekey == '**':
            found = self._recursive_seek('*/' + remkey, searchArea)
            found[''] = self._recursive_seek('*/' + key, searchArea)
        elif primekey == '*':
            localkeys = {*searchArea, *searchArea.attrs}
            searchkeys = [
                localkey + '/' + remkey \
                    for localkey in localkeys
                ]
            found = dict()
            for searchkey in searchkeys:
                try:
                    found[searchkey.split('/')[0]] = \
                        self._recursive_seek(searchkey, searchArea)
                except:
                    pass
        else:
            try:
                found = searchArea[primekey]
            except:
                found = searchArea.attrs[primekey]
            if not remkey == '':
                found = self._recursive_seek(remkey, found)
        return found

    def _pre_seekresolve(self, inp):
        # expects h5filewrap
        if type(inp) is h5py.Group:
            out = _ADDRESSTAG_ + inp.name
        elif type(inp) is h5py.Dataset:
            out = inp[...]
        elif type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._pre_seekresolve(sub)
        else:
            out = inp
        return out

    @disk.h5filewrap
    def _seek(self, key):
        return self._pre_seekresolve(self._recursive_seek(key))

    @staticmethod
    def _process_tag(inp, tag):
        processed = inp[len(tag):]
        assert len(processed) > 0
        return processed

    def _seekresolve(self, inp):
        if type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._seekresolve(sub)
        elif type(inp) is np.ndarray:
            out = inp
        elif type(inp) is str:
            global \
                _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
                _BYTESTAG_, _STRINGTAG_, _EVALTAG_
            if inp.startswith(_BUILTTAG_):
                processed = self._process_tag(inp, _BUILTTAG_)
                out = self._builtsModule.load(processed, self.name, self.path)
            elif inp.startswith(_CLASSTAG_):
                processed = self._process_tag(inp, _CLASSTAG_)
                out = disk.local_import_from_str(processed).CLASS
            elif inp.startswith(_ADDRESSTAG_):
                processed = self._process_tag(inp, _ADDRESSTAG_)
                splitAddr = [*processed.split('/'), '*']
                if splitAddr[0] == '': splitAddr.pop(0)
                out = self[tuple(splitAddr)]
            elif inp.startswith(_BYTESTAG_):
                processed = self._process_tag(inp, _BYTESTAG_)
                bytesStr = ast.literal_eval(processed)
                assert len(processed) > 0
                out = pickle.loads(bytesStr)
            elif inp.startswith(_EVALTAG_):
                processed = self._process_tag(inp, _EVALTAG_)
                assert len(processed) > 0
                out = ast.literal_eval(processed)
                if type(out) in {list, tuple, frozenset}:
                    procOut = list()
                    for item in out:
                        procOut.append(self._seekresolve(item))
                    out = type(out)(procOut)
            elif inp.startswith(_STRINGTAG_):
                processed = self._process_tag(inp, _STRINGTAG_)
                assert len(processed) > 0
                out = processed
            else:
                raise TypeError
        return out

    @staticmethod
    def _process_fetch(inFetch, context):
        inDict = inFetch(context)
        outs = set()
        for key, result in inDict.items():
            superkey = key.split('/')[0]
            indices = None
            try:
                if result:
                    indices = '...'
            except ValueError:
                if np.all(result):
                    indices = '...'
                elif np.any(result):
                    countsPath = '/' + '/'.join((
                        superkey,
                        'outputs',
                        'count'
                        ))
                    counts = context(countsPath)
                    indices = counts[result.flatten()]
                    indices = tuple(indices)
            except:
                raise TypeError
            if not indices is None:
                outs.add((superkey, indices))
        return outs

    def _gettuple(self, inp):
        if len(set([type(subInp) for subInp in inp])) == 1:
            inpType = type(inp[0])
            if not inpType in self._getmethods:
                raise TypeError
            if inpType is type(Ellipsis):
                raise TypeError
        else:
            raise TypeError
        method = self._getmethods[inpType]
        if inpType is str:
            return method(self, '/'.join(inp))
        else:
            outs = tuple([method(self, subInp) for subInp in inp])
            if inpType is Fetch:
                return reduce(operator.__and__, outs, 1)
            else:
                return outs

    def _getstr(self, key):
        resolved = self._seekresolve(self._seek(key))
        if type(resolved) is dict:
            out = utilities.flatten(resolved, sep = '/')
        else:
            out = resolved
        return out

    def _getfetch(self, fetch):
        processed = self._process_fetch(fetch, self.__getitem__)
        sources = ('Scope', (fetch,))
        return Scope(processed, sources = sources)

    def _getslice(self, inp):
        if type(inp.start) is Scope:
            inScope = inp.start
        elif type(inp.start) is Fetch:
            inScope = self.__getitem__(inp.start)
        else:
            raise TypeError
        if not type(inp.stop) in {str, tuple}:
            raise TypeError
        return self.pull(inScope, inp.stop)

    def _getellipsis(self, inp):
        return self._getfetch(Fetch('**'))

    _getmethods = {
        tuple: _gettuple,
        str: _getstr,
        Fetch: _getfetch,
        slice: _getslice,
        type(Ellipsis): _getellipsis
        }

    def __getitem__(self, inp):
        if type(inp) in self._getmethods:
            return self._getmethods[type(inp)](self, inp)
        else:
            if type(inp) is Scope:
                raise ValueError(
                    "Must provide a key to pull data from a scope"
                    )
            raise TypeError("Input not recognised: ", inp)

    context = __getitem__
