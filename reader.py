import h5py
from functools import partial
from functools import reduce
import operator
import os
import numpy as np
import ast
import pickle

from . import disk
from . import mpi
from . import utilities
from .fetch import Fetch
from .scope import Scope
from .globevars import \
    _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
    _BYTESTAG_, _STRINGTAG_, _EVALTAG_

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

    def _recursive_seek(self, key, searchArea = None):
        # expects h5readwrap
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
        # expects h5readwrap
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

    @disk.h5readwrap
    @mpi.dowrap
    def _seek(self, key):
        return self._pre_seekresolve(self._recursive_seek(key))

    @staticmethod
    def _process_tag(inp, tag):
        processed = inp[len(tag):]
        assert len(processed) > 0, "Len(processed) not greater than zero!"
        return processed

    def _seekresolve(self, inp, hard = False, **kwargs):
        if type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._seekresolve(sub, hard = hard)
        elif type(inp) is np.ndarray:
            out = inp
        elif type(inp) is str:
            global \
                _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
                _BYTESTAG_, _STRINGTAG_, _EVALTAG_
            if inp.startswith(_BUILTTAG_):
                processed = self._process_tag(inp, _BUILTTAG_)
                if hard:
                    out = self._builtsModule.load(
                        processed,
                        self.name,
                        self.path
                        )
                else:
                    out = processed
            elif inp.startswith(_CLASSTAG_):
                processed = self._process_tag(inp, _CLASSTAG_)
                if hard:
                    out = disk.local_import_from_str(processed).CLASS
                else:
                    out = self._builtsModule.make_hash(processed)
            elif inp.startswith(_ADDRESSTAG_):
                processed = self._process_tag(inp, _ADDRESSTAG_)
                splitAddr = [*processed.split('/'), '*']
                if splitAddr[0] == '': splitAddr.pop(0)
                out = self._getitem(tuple(splitAddr), hard = hard)
            elif inp.startswith(_BYTESTAG_):
                processed = self._process_tag(inp, _BYTESTAG_)
                bytesStr = ast.literal_eval(processed)
                out = pickle.loads(bytesStr)
            elif inp.startswith(_EVALTAG_):
                processed = self._process_tag(inp, _EVALTAG_)
                out = ast.literal_eval(processed)
                if type(out) in {list, tuple, frozenset}:
                    procOut = list()
                    for item in out:
                        procOut.append(self._seekresolve(item, hard = hard))
                    out = type(out)(procOut)
            elif inp.startswith(_STRINGTAG_):
                processed = self._process_tag(inp, _STRINGTAG_)
                out = processed
            else:
                raise TypeError
        return out

    @staticmethod
    def _process_fetch(inFetch, context, scope = None, **kwargs):
        inDict = inFetch(context)
        outs = set()
        if scope is None:
            checkkey = lambda key: True
        elif type(scope) is Scope:
            checkkey = lambda key: key in scope.keys()
        else:
            raise TypeError
        for key, result in sorted(inDict.items()):
            superkey = key.split('/')[0]
            if checkkey(superkey):
                indices = None
                try:
                    if result:
                        indices = '...'
                except ValueError:
                    if np.all(result):
                        indices = '...'
                    elif np.any(result):
                        countsPath = '/'.join((
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
            else:
                pass
        return outs

    def _gettuple(self, inp, **kwargs):
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
            return method(self, '/'.join(inp), **kwargs)
        else:
            outs = tuple([method(self, subInp, **kwargs) for subInp in inp])
            if inpType is Fetch:
                return reduce(operator.__and__, outs, 1)
            else:
                return outs

    def _getstr(self, key, hard = False, **kwargs):
        resolved = self._seekresolve(self._seek(key), hard = hard)
        if type(resolved) is dict:
            out = utilities.flatten(resolved, sep = '/')
        else:
            out = resolved
        return out

    def _getfetch(self, fetch, scope = None, **kwargs):
        processed = self._process_fetch(fetch, self.__getitem__, scope = scope)
        sources = ('Scope', (fetch,))
        newScope = Scope(processed, sources = sources)
        if scope is None:
            return newScope
        else:
            return scope & newScope

    def _getslice(self, inp, **kwargs):
        if type(inp.start) is Scope:
            inScope = inp.start
        elif type(inp.start) is Fetch:
            inScope = self[inp.start]
        else:
            raise TypeError
        if type(inp.stop) is Fetch:
            newScope = self._getfetch(inp.stop, scope = inScope, **kwargs)
            if inp.step is None:
                return newScope
            else:
                return self._getslice(slice(newScope, inp.step))
        elif type(inp.stop) in {str, tuple}:
            if not inp.step is None:
                raise TypeError
            supp = inp.stop
            arrList = []
            for hashID, retrieveCounts in inScope:
                data = self[hashID, supp]
                if retrieveCounts == '...':
                    arrList.append(data)
                else:
                    if not type(data) is np.ndarray:
                        raise TypeError
                    counts = self[hashID, 'outputs', 'count']
                    maskArr = np.isin(
                        counts,
                        retrieveCounts,
                        assume_unique = True
                        )
                    arr = data[maskArr]
                    arrList.append(arr)
            allTuple = tuple(arrList)
            return allTuple
        else:
            raise TypeError

    def _getellipsis(self, inp, **kwargs):
        return self._getfetch(Fetch('**'))

    _getmethods = {
        tuple: _gettuple,
        str: _getstr,
        Fetch: _getfetch,
        slice: _getslice,
        type(Ellipsis): _getellipsis
        }

    def _getitem(self, inp, hard = False):
        if type(inp) is tuple:
            if len(inp) == 1:
                inp = inp[0]
        if type(inp) in self._getmethods:
            return self._getmethods[type(inp)](self, inp, hard = hard)
        else:
            if type(inp) is Scope:
                raise ValueError(
                    "Must provide a key to pull data from a scope"
                    )
            raise TypeError("Input not recognised: ", inp)

    def __getitem__(self, inp):
        return self._getitem(inp, hard = False)

    def __call__(self, *inp):
        return self._getitem(inp, hard = True)

    context = __getitem__
