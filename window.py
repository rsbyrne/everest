import h5py
import operator
import numpy as np
from functools import partial
from functools import reduce
from collections.abc import Set
from collections.abc import Hashable

import time
import os

from . import disk
from . import _specialnames

# from . import frame
#
# def frame_name(frameID, outputPath):
#     return os.path.join(outputPath, frameID) + '.' + _specialnames.FRAME_EXT

class Fetch:

    operations = operator.__dict__
    operations[None] = lambda *args: True

    def __init__(
            self,
            *args,
            operation = None,
            options = []
            ):
        self.args = args
        self.operation = operation
        self.options = options

    def __call__(self, context = None):
        if context is None:
            context = lambda *inp: inp
        try:
            args = context(*self.args)
            if len(args) == 0:
                output = np.array(True)
            else:
                args = [np.array(arg) for arg in args]
                output = np.array(
                    self.operations[self.operation](*args)
                    ).flatten()
        except KeyError:
            output = np.array(False)
        if 'invert' in self.options:
            return ~output
        else:
            return output

    def __lt__(self, *args):
        return Fetch(*self.args, *args, operation = 'lt')
    def __le__(self, *args):
        return Fetch(*self.args, *args, operation = 'le')
    def __eq__(self, *args):
        return Fetch(*self.args, *args, operation = 'eq')
    def __ne__(self, *args):
        return Fetch(*self.args, *args, operation = 'ne')
    def __ge__(self, *args):
        return Fetch(*self.args, *args, operation = 'ge')
    def __gt__(self, *args):
        return Fetch(*self.args, *args, operation = 'gt')
    def __invert__(self):
        return Fetch(
            *self.args,
            operation = self.operation,
            options = ['invert']
            )
    def __add__(self, arg):
        return Pending(self, arg, function = Scope.union)
    def __sub__(self, arg):
        return Pending(self, arg, function = Scope.difference)
    def __mul__(self, arg):
        return Pending(self, arg, function = Scope.intersection)
    def __div__(self, arg):
        return Pending(self, arg, function = Scope.symmetric)

class Pending:
    def __init__(self, *args, function = None):
        self.args = args
        self.function = function
    def __call__(self, getscopesFn):
        scopes = [getscopesFn(arg) for arg in self.args]
        return self.function(*scopes)
    def __add__(self, arg):
        return Pending(self, arg, function = Scope.union)
    def __sub__(self, arg):
        return Pending(self, arg, function = Scope.difference)
    def __mul__(self, arg):
        return Pending(self, arg, function = Scope.intersection)
    def __div__(self, arg):
        return Pending(self, arg, function = Scope.symmetric)

class Scope(Set, Hashable):

    __hash__ = Set._hash

    def __new__(cls, iterable):
        selfobj = super(Scope, cls).__new__(Scope)
        cleaned_iterable = cls._process_scope_inputs(iterable)
        selfobj._set = frozenset(cleaned_iterable)
        return selfobj

    def keys(self):
        return set([key for key, val in self._set])

    @staticmethod
    def _process_scope_inputs(iterable):
        cleaned_iterable = []
        for key, val in iterable:
            if val == '...' or type(val) is tuple:
                pass
    #         elif type(val) is np.ndarray:
    #             val = tuple(val)
            else:
                raise TypeError
            cleaned_iterable.append((key, val))
        return cleaned_iterable

    @classmethod
    def _process_args(cls, *args):
        if not all([type(arg) is cls for arg in args]):
            raise TypeError
        allSets = [arg._set for arg in args]
        allDicts = [dict(subSet) for subSet in allSets]
        commonkeys = set.intersection(
            *[set(subDict) for subDict in allDicts]
            )
        uncommonkeys = [
            key \
                for subDict in allDicts \
                    for key in subDict.keys()
            ]
        return allDicts, commonkeys, uncommonkeys

    @classmethod
    def union(cls, *args):
        allDicts, commonkeys, uncommonkeys = cls._process_args(*args)
        outDict = dict()
        for subDict in allDicts:
            outDict.update(subDict)
        for key in commonkeys:
            allData = tuple(
                np.array(subDict[key]) \
                    for subDict in allDicts \
                        if not subDict[key] == _specialnames.ALL_COUNTS_FLAG
                )
            if len(allData) > 0:
                outDict[key] = tuple(
                    reduce(
                        np.union1d,
                        allData
                        )
                    )
            else:
                outDict[key] = '...'
        outScope = Scope(outDict.items())
        return outScope

    @classmethod
    def difference(cls, *args):
        allDicts, commonkeys, uncommonkeys = cls._process_args(*args)
        if not len(allDicts) == 2:
            raise ValueError
        primeDict, opDict = allDicts
        prime_uncommonkeys = {
            key \
                for key in primeDict \
                    if not key in commonkeys
            }
        outDict = dict()
        for key in prime_uncommonkeys:
            outDict[key] = primeDict[key]
        for key in commonkeys:
            primeData, opData = primeDict[key], opDict[key]
            primeAll = primeData == _specialnames.ALL_COUNTS_FLAG
            opAll = opData == _specialnames.ALL_COUNTS_FLAG
            if opAll and primeAll:
                pass
            elif opAll:
                outDict[key] = primeDict[key]
            elif primeAll:
                outDict[key] = opDict[key]
            else:
                # solution by Divakar @ stackoverflow
                dims = np.maximum(opData.max(0), primeData.max(0)) + 1
                out = primeData[ \
                    ~np.in1d(
                        np.ravel_multi_index(primeData.T, dims),
                        np.ravel_multi_index(opData.T, dims)
                        )
                    ]
                if len(out) > 0:
                    outDict[key] = tuple(out)
        outScope = Scope(outDict.items())
        return outScope

    @classmethod
    def intersection(cls, *args):
        allDicts, commonkeys, uncommonkeys = cls._process_args(*args)
        outDict = dict()
        for key in commonkeys:
            allData = tuple(
                np.array(subDict[key]) \
                    for subDict in allDicts \
                        if not subDict[key] == _specialnames.ALL_COUNTS_FLAG
                )
            if len(allData) > 0:
                intTuple = tuple(
                    reduce(
                        np.intersect1d,
                        allData
                        )
                    )
                if len(intTuple) > 0:
                    outDict[key] = intTuple
            else:
                outDict[key] = '...'
        outScope = Scope(outDict.items())
        return outScope

    @classmethod
    def symmetric(cls, *args):
        raise Exception("Not supported yet!")

    def __add__(self, arg):
        return self.union(self, arg)
    def __sub__(self, arg):
        return self.difference(self, arg)
    def __mul__(self, arg):
        return self.intersection(self, arg)
    def __div__(self, arg):
        return self.symmetric(self, arg)
    def __repr__(self):
        return "Scope({0})".format(set(self._set))
    def __reduce__(self):
        return (Scope, (self._set,))
    def __getattr__(self, attr):
        return getattr(self._set, attr)
    def __contains__(self, item):
        return item in self._set
    def __len__(self):
        return len(self._set)
    def __iter__(self):
        return iter(self._set)

class Reader:

    h5file = None

    def __init__(
            self,
            h5filename
            ):
        self.h5filename = h5filename
        self.file = partial(h5py.File, h5filename, 'r')

    @disk.h5filewrap
    def full_scope(self):
        scopelets = set()
        for superkey in self.h5file:
            scopelets.add((superkey, '...'))
        return Scope(scopelets)

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
        for superkey, scopeCounts in sorted(scope):
            thisGroup = self.h5file[superkey]
            thisTargetDataset = thisGroup[key]
            if scopeCounts == '...':
                arr = thisTargetDataset[...]
            else:
                thisCountsDataset = thisGroup[_specialnames.COUNTS_FLAG]
                maskArr = np.isin(
                    thisCountsDataset,
                    scopeCounts,
                    assume_unique = True
                    )
                arr = thisTargetDataset[maskArr]
            arrList.append(arr)
        allArr = np.concatenate(arrList)
        return allArr

    def view_attrs(self, scope = None):
        if scope is None:
            scope = self.full_scope()
        return self._view_attrs(scope)

    @disk.h5filewrap
    def _view_attrs(self, scope):
        outDict = dict()
        for superkey, scopeCounts in scope:
            builtGroup = self.h5file[superkey]
            for key in builtGroup.attrs:
                if not key in outDict:
                    outDict[key] = dict()
                keyval = builtGroup.attrs[key]
                if not keyval in outDict[key]:
                    outDict[key][keyval] = set()
                outDict[key][keyval].add((superkey, scopeCounts))
        for key in outDict:
            for subKey in outDict[key]:
                outDict[key][subKey] = Scope(outDict[key][subKey])
        return outDict

    @staticmethod
    def summary_of_dict(allDict):
        for key in sorted(allDict):
            print(key)
            for subKey in sorted(allDict[key]):
                print(subKey)

    @disk.h5filewrap
    def sort_by_attr(self, key, scope = None):
        if scope is None:
            superkeys = self.h5file.keys()
        else:
            superkeys = [key for key, val in scope]
        outDict = dict()
        for superkey in superkeys:
            builtGroup = self.h5file[superkey]
            if key in builtGroup.attrs:
                keyval = builtGroup.attrs[key]
                if not keyval in outDict:
                    outDict[keyval] = set()
                newEntry = (superkey, '...')
                outDict[keyval].add(newEntry)
        for key in outDict:
            outDict[key] = Scope(outDict[key])
        return sorted(outDict.items())

    # def pull_attrs(self, scope, keys = )

    def __getitem__(self, inp):
        if type(inp) is Fetch:
            return self._get_fetch(inp)
        elif type(inp) is Pending:
            return inp(self.__getitem__)
        elif inp is Ellipsis:
            return self._get_fetch(Fetch())
        elif type(inp) is Scope:
            raise Exception("That behaviour not supported yet")
        else:
            raise TypeError

    def _context(self, superkey, *args):
        if len(args) == 0:
            return tuple()
        else:
            args = list(args)
            key = args.pop(0)
            splitkey = key.split('/')
            try: out = self.h5file[superkey] \
                [key]
            except: out = self.h5file[superkey] \
                ['/'.join(splitkey[:-1])].attrs[splitkey[-1]]
            return (out, *args)

    @disk.h5filewrap
    def _get_fetch(self, fetch):
        outs = set()
        for superkey in self.h5file:
            context = partial(
                self._context,
                superkey
                )
            result = fetch(context) # THIS IS THE SLOWEST BIT
            indices = None
            try:
                if result:
                    indices = '...'
            except ValueError:
                if np.all(result):
                    indices = '...'
                elif np.any(result):
                    indices = tuple(
                        self.h5file\
                            [superkey] \
                            ['outs'] \
                            [_specialnames.COUNTS_FLAG] \
                            [result]
                        )
            except:
                raise TypeError
            if not indices is None:
                outs.add((superkey, indices))
        outs = Scope(outs)
        return outs
