import h5py
from functools import partial
from functools import reduce
import operator
import os
import numpy as np
import ast
import pickle

from . import disk
H5Manager = disk.H5Manager
from . import mpi
from . import utilities
make_hash = utilities.make_hash
from .fetch import Fetch
from .scope import Scope
from .globevars import \
    _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
    _BYTESTAG_, _STRINGTAG_, _EVALTAG_, \
    _GROUPTAG_
from .exceptions import EverestException, InDevelopmentError

class PathNotInFrameError(EverestException, KeyError):
    pass
class NotGroupError(EverestException, KeyError):
    pass

class Proxy:
    def __init__(self):
        pass

class ClassProxy(Proxy):
    def __init__(self, script):
        self.script = script
        super().__init__()
    def __call__(self):
        return disk.local_import_from_str(self.script).CLASS
    def __repr__(self):
        return _CLASSTAG_ + make_hash(self.script)

# class BuiltProxy(Proxy):
#     def __init__(self, cls, **inputs):
#         if type(cls) is ClassProxy:
#             cls = cls()
#         from .builts import _get_info
#         ignoreme, ignoreme, inputsHash, instanceHash, hashID = \
#             _get_info(cls, inputs)
#         self.cls, self.inputs, self.hashID = cls, inputs, hashID
#         super().__init__()
#     def __call__(self):
#         return self.cls(**self.inputs)
#     def __repr__(self):
#         return _BUILTTAG_ + self.hashID

class Reader(H5Manager):

    def __init__(
            self,
            name,
            path,
            *cwd
            ):
        self.name, self.path = name, path
        self.h5filename = os.path.join(os.path.abspath(path), name + '.frm')
        self.file = partial(h5py.File, self.h5filename, 'r')
        super().__init__(*cwd)

    def _recursive_seek(self, key, searchArea = None):
        # expects h5filewrap
        if searchArea is None:
            searchArea = self.h5file
        # print("Seeking", key, "from", searchArea)
        splitkey = key.split('/')
        try:
            if splitkey[0] == '':
                splitkey = splitkey[1:]
            if splitkey[-1] == '':
                splitkey = splitkey[:-1]
        except IndexError:
            raise Exception("Bad key: " + str(key) +  ', ' + str(type(key)))
        primekey = splitkey[0]
        remkey = '/'.join(splitkey[1:])
        if primekey == '**':
            raise InDevelopmentError
            # found = self._recursive_seek('*/' + remkey, searchArea)
            # found[''] = self._recursive_seek('*/' + key, searchArea)
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
                except KeyError:
                    pass
        else:
            try:
                try:
                    found = searchArea[primekey]
                except KeyError:
                    try:
                        found = searchArea.attrs[primekey]
                    except KeyError:
                        raise PathNotInFrameError(
                            "Path " \
                            + primekey \
                            + " does not exist in search area " \
                            + str(searchArea) \
                            )
            except ValueError:
                raise Exception("Value error???", primekey, type(primekey))
            if not remkey == '':
                if type(found) is h5py.Group:
                    found = self._recursive_seek(remkey, found)
                else:
                    raise NotGroupError()
        return found

    def _pre_seekresolve(self, inp):
        # expects h5filewrap
        if type(inp) is h5py.Group:
            out = _GROUPTAG_ + inp.name
        elif type(inp) is h5py.Dataset:
            out = inp[...]
        elif type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._pre_seekresolve(sub)
        else:
            out = inp
        return out

    @mpi.dowrap
    def _seek(self, key):
        presought = self._recursive_seek(key)
        sought = self._pre_seekresolve(presought)
        return sought

    @staticmethod
    def _process_tag(inp, tag):
        processed = inp[len(tag):]
        assert len(processed) > 0, "Len(processed) not greater than zero!"
        return processed

    @disk.h5filewrap
    def load(self, hashID):
        inputs = self.__getitem__('/' + self.join(hashID, 'inputs'))
        typeHash = self.__getitem__('/' + self.join(hashID, 'typeHash'))
        cls = self.__getitem__(
            '/' + self.join('_globals_', 'classes', typeHash)
            )
        built = cls(**inputs)
        assert built.hashID == hashID
        built.anchor(self.name, self.path)
        return built

    def _seekresolve(self, inp):
        if type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._seekresolve(sub)
            return out
        elif type(inp) is np.ndarray:
            return inp
        elif type(inp) is str:
            global \
                _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
                _BYTESTAG_, _STRINGTAG_, _EVALTAG_
            if inp.startswith(_BUILTTAG_):
                hashID = self._process_tag(inp, _BUILTTAG_)
                return self.load(hashID)
            elif inp.startswith(_CLASSTAG_):
                script = self._process_tag(inp, _CLASSTAG_)
                proxy = ClassProxy(script)
                cls = proxy()
                return cls
            elif inp.startswith(_ADDRESSTAG_):
                address = self._process_tag(inp, _ADDRESSTAG_)
                return self._getstr(address)
            elif inp.startswith(_GROUPTAG_):
                groupname = self._process_tag(inp, _GROUPTAG_)
                return self._getstr(os.path.join(groupname, '*'))
            elif inp.startswith(_BYTESTAG_):
                processed = self._process_tag(inp, _BYTESTAG_)
                bytesStr = ast.literal_eval(processed)
                return pickle.loads(bytesStr)
            elif inp.startswith(_EVALTAG_):
                processed = self._process_tag(inp, _EVALTAG_)
                out = ast.literal_eval(processed)
                if type(out) in {list, tuple, frozenset}:
                    procOut = list()
                    for item in out:
                        procOut.append(self._seekresolve(item))
                    out = type(out)(procOut)
                return out
            elif inp.startswith(_STRINGTAG_):
                return self._process_tag(inp, _STRINGTAG_)
            else:
                raise ValueError(inp)
        else:
            raise TypeError(type(inp))

    def getfrom(self, *keys):
        return self.__getitem__(os.path.join(*keys))

    def _getstr(self, key):
        if type(key) in {tuple, list}:
            key = self.join(*key)
        key = os.path.abspath(os.path.join(self.cwd, key))
        # print("Getting string:", key)
        sought = self._seek(key)
        resolved = self._seekresolve(sought)
        return resolved

    def _getfetch(self, fetch, scope = None):
        return fetch(self.__getitem__, scope)

    def _getslice(self, inp):
        if type(inp.start) is Scope:
            inScope = inp.start
        elif type(inp.start) is Fetch:
            inScope = self[inp.start]
        else:
            raise TypeError
        if type(inp.stop) is Fetch:
            newScope = self._getfetch(inp.stop, scope = inScope)
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

    def _getellipsis(self, inp):
        return self._getfetch(Fetch('**'))

    def _getscope(self, inp):
        raise ValueError(
            "Must provide a key to pull data from a scope"
            )

    _getmethods = {
        str: _getstr,
        Fetch: _getfetch,
        slice: _getslice,
        Scope: _getscope,
        type(Ellipsis): _getellipsis
        }

    def _getitem(self, inp):
        if not type(inp) in self._getmethods:
            raise TypeError("Input not recognised: ", inp)
        return self._getmethods[type(inp)](self, inp)

    @disk.h5filewrap
    def __getitem__(self, inp):
        if type(inp) is tuple:
            return [self._getitem(sub) for sub in inp]
        else:
            return self._getitem(inp)
