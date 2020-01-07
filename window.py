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
from . import utilities

# from . import frame
#
# def frame_name(frameID, outputPath):
#     return os.path.join(outputPath, frameID) + '.' + _specialnames.FRAME_EXT

class Fetch:

    _fnDict = {}
    _fnDict.update(operator.__dict__)

    def __init__(
            self,
            *args,
            operation = None,
            opTag = None
            ):
        if type(operation) is str:
            opTag = operation
            operation = self._fnDict[operation]
        elif opTag is None:
            opTag = 'anon'

        self.args = args
        self.operation = operation
        self.opTag = opTag

    def __reduce__(self):
        return (Fetch, (self.args, self.operation, self.opTag))

    @classmethod
    def _operate(cls, *args, operation = None, context = None):
        operands = []
        for arg in args:
            if type(arg) is Fetch:
                opVals = arg(context)
            else:
                opVals = np.array(arg)
            operands.append(opVals)
        dictOperands = [
            operand for operand in operands if type(operand) is dict
            ]
        allkeys = list()
        for dictOperand in dictOperands:
            allkeys.extend(list(dictOperand.keys()))
        allkeys = set(allkeys)
        filteredOperands = []
        for operand in operands:
            if type(operand) is dict:
                missingKeys = [
                    key \
                        for key in allkeys \
                            if not key in operand
                    ]
                for key in missingKeys:
                    operand[key] = np.nan
            else:
                operand = {key: operand for key in allkeys}
            filteredOperands.append(operand)
        operands = filteredOperands
        outDict = dict()
        for key in allkeys:
            keyops = [operand[key] for operand in operands]
            try:
                evalVal = operation(*keyops)
            except TypeError:
                evalVal = None
            outDict[key] = evalVal
        return outDict

    def __call__(self, context):
        if self.operation is None:
            out = context(self.args[0])
        else:
            out = self._operate(
                *self.args,
                operation = self.operation,
                context = context
                )
        return out

    def fn(self, operation, args):
        return Fetch(
            *(self, *args),
            operation = operation,
            opTag = None
            )

    def __lt__(*args): # <
        return Fetch(*args, operation = '__lt__')
    def __le__(*args): # <=
        return Fetch(*args, operation = '__le__')
    def __eq__(*args): # ==
        return Fetch(*args, operation = '__eq__')
    def __ne__(*args): # !=
        return Fetch(*args, operation = '__ne__')
    def __ge__(*args): # >=
        return Fetch(*args, operation = '__ge__')
    def __gt__(*args): # >
        return Fetch(*args, operation = '__gt__')
    def __neg__(*args): # -
        return Fetch(*args, operation = '__neg__')
    def __abs__(*args): # abs
        return Fetch(*args, operation = '__abs__')
    def __add__(*args): # +
        return Fetch(*args, operation = '__add__')
    def __sub__(*args): # -
        return Fetch(*args, operation = '__sub__')
    def __mul__(*args): # *
        return Fetch(*args, operation = '__mul__')
    def __div__(*args): # /
        return Fetch(*args, operation = '__div__')
    def __pow__(*args): # **
        return Fetch(*args, operation = '__pow__')
    def __floordiv__(*args): # //
        return Fetch(*args, operation = '__floordiv__')
    def __mod__(*args): # %
        return Fetch(*args, operation = '__mod__')
    def __contains__(*args): # in
        return Fetch(*args, operation = '__contains__')
    def __invert__(*args): # ~
        return Fetch(*args, operation = '__invert__')

    def __or__(*args): # |
        return Fetch(
            *args,
            operation = np.logical_or,
            opTag = '__union__'
            )
    @staticmethod
    def _diff_op(arg1, arg2):
        return np.logical_and(arg1, ~arg2)
    def __lshift__(*args): # <<
        return Fetch(
            *args,
            operation = args[0]._diff_op,
            opTag = '__difference__'
            )
    def __rshift__(*args): # <<
        return Fetch(
            *args[::-1],
            operation = args[0]._diff_op,
            opTag = '__difference__'
            )
    def __and__(*args): # &
        return Fetch(
            *args,
            operation = np.logical_and,
            opTag = '__intersection__'
            )
    def __xor__(*args): # ^
        return Fetch(
            *args,
            operation = np.logical_xor,
            opTag = '__symmetric__'
            )

class Scope(Set, Hashable):

    __hash__ = Set._hash
    contents = set()

    def __new__(cls, inp, context = None):
        selfobj = super(Scope, cls).__new__(Scope)
        if type(inp) is Fetch:
            unclean_iterable = cls._process_fetch(inp, context)
        else:
            unclean_iterable = inp
        cleaned_iterable = cls._process_iterable(unclean_iterable)
        selfobj._set = frozenset(cleaned_iterable)
        return selfobj

    def keys(self):
        return set([key for key, val in self._set])

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
                    countsPath = '/'.join((
                        superkey,
                        'outs',
                        _specialnames.COUNTS_FLAG
                        ))
                    counts = context(countsPath)
                    indices = counts[result.flatten()]
                    indices = tuple(indices)
            except:
                raise TypeError
            if not indices is None:
                outs.add((superkey, indices))
        self.contents.add((inFetch, context))
        return outs

    @staticmethod
    def _process_iterable(iterable):
        cleaned_iterable = []
        for key, val in iterable:
            if val == '...' or type(val) is tuple:
                pass
            # elif type(val) is np.ndarray:
            #     val = tuple(val)
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
        outScope.contents.add((inFetch, context))
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

    @classmethod
    def _operation(cls, *args, opFn = None):
        if all([type(arg) is Scope for arg in args]):
            return opFn(*args)
        else:
            return Pending(*args, function = opFn)

    def __or__(self, arg):
        return self._operation(self, arg, opFn = self.union)
    def __lshift__(self, arg):
        return self._operation(self, arg, opFn = self.difference)
    def __rshift__(self, arg):
        return self._operation(arg, self, opFn = self.difference)
    def __and__(self, arg):
        return self._operation(self, arg, opFn = self.intersection)
    def __xor__(self, arg):
        return self._operation(self, arg, opFn = self.symmetric)

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
            thisTargetDataset = thisGroup['outs'][key]
            if scopeCounts == '...':
                arr = thisTargetDataset[...]
            else:
                thisCountsDataset = thisGroup['outs'][_specialnames.COUNTS_FLAG]
                maskArr = np.isin(
                    thisCountsDataset,
                    scopeCounts,
                    assume_unique = True
                    )
                slicer = (
                    maskArr,
                    *[slice(1) for i in range(1, len(thisTargetDataset.shape))]
                    )
                arr = thisTargetDataset[slicer]
            arrList.append(arr)
        try:
            allArr = np.concatenate(arrList)
            return allArr
        except ValueError:
            allTuple = tuple(arrList)
            return allTuple

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

    @classmethod
    def _seek(cls, key, searchArea):
        # expects h5filewrap
        splitkey = key.split('/')
        primekey = splitkey[0]
        remkey = '/'.join(splitkey[1:])
        if primekey == '**':
            found = cls._seek('*/' + remkey, searchArea)
            found[''] = cls._seek('*/' + key, searchArea)
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
                        cls._seek(searchkey, searchArea)
                except:
                    pass
        else:
            try:
                found = searchArea[primekey]
            except:
                found = searchArea.attrs[primekey]
            if not remkey == '':
                found = cls._seek(remkey, found)
        return found

    def _seekresolve(self, toResolve):
        # expects h5filewrap
        if type(toResolve) is dict:
            out = dict()
            for key, val in toResolve.items():
                out[key] = self._seekresolve(val)
        elif type(toResolve) is h5py.Group:
            out = toResolve.name
        elif type(toResolve) is h5py.Dataset:
            out = np.array(toResolve)
        elif type(toResolve) is h5py.Reference:
            out = self.h5file[toResolve].attrs['hashID']
        elif isinstance(toResolve, np.generic):
            out = np.asscalar(toResolve)
        else:
            out = toResolve
        return out

    def _gettuple(self, inp):
        return [self.__getitem__(subInp) for subInp in inp]

    @disk.h5filewrap
    def _getstr(self, key):
        if key == '':
            key = '**'
        elif key[0] == '/':
            key = key[1:]
        elif not key[:2] == '**':
            key = '**/' + key
        sought = self._seek(key, self.h5file)
        resolved = self._seekresolve(sought)
        if type(resolved) is dict:
            out = utilities.flatten(resolved, sep = '/')
        else:
            out = resolved
        return out

    def _getfetch(self, fetch):
        return Scope(fetch, self.__getitem__)

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
        return self._getfetch(Fetch('/*'))

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
