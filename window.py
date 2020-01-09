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
            opTag = 'Fetch'

        self.args = args
        self.operation = operation
        self.opTag = opTag
        self.ID = str(self)

    def __repr__(self):
        ID = self.opTag + '({0})'.format(
            ', '.join([
                str(arg) \
                    for arg in self.args
                ])
            )
        return ID

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

    def __new__(cls, inp, sources = None):
        if type(inp) is Scope:
            return inp
        else:
            selfobj = super().__new__(Scope)
            if sources is None:
                ID = 'anon'
            else:
                opTag, sourceargs = sources
                ID = opTag + '({0})'.format(
                    ', '.join([
                        sourcearg.ID \
                            for sourcearg in sourceargs
                        ])
                    )
            selfobj.ID = ID
            selfobj.sources = sources
            selfobj._set = frozenset(inp)
            return selfobj

    def keys(self):
        return set([key for key, val in self._set])

    def __repr__(self):
        return 'Scope(\n{0}\n)'.format(
            '\n'.join([
                str(row) \
                    for row in set(self._set)
                ])
            )
    def __reduce__(self):
        return Scope, (self._set, self.sources)
    def __getattr__(self, attr):
        return getattr(self._set, attr)
    def __contains__(self, item):
        return item in self._set
    def __len__(self):
        return len(self._set)
    def __iter__(self):
        return iter(self._set)

    def rekey(self, mapAttr, context):
        newlist = []
        for hashID, counts in list(self):
            newID = list(context(Fetch(mapAttr) == hashID))[0][0]
            newlist.append((newID, counts))
        return Scope(newlist, ('rekey_' + mapAttr, [self,]))

    @classmethod
    def _process_args(cls, *args):
        allScopes = [cls(arg) for arg in args]
        allSets = [subScope._set for subScope in allScopes]
        allDicts = [dict(subSet) for subSet in allSets]
        commonkeys = set.intersection(
            *[set(subDict) for subDict in allDicts]
            )
        uncommonkeys = [
            key \
                for subDict in allDicts \
                    for key in subDict.keys()
            ]
        return allScopes, allDicts, commonkeys, uncommonkeys

    @classmethod
    def invert(cls, arg):
        inScope = cls(arg)
        scopeDict = dict(inScope._set)
        outDict = {}
        for key in sorted(inScope.keys()):
            outDict[key] = tuple(
                np.sort(
                    np.array(scopeDict[key]) - int(1e18)
                    )
                )
        return cls(frozenset(outDict.items()), ('__invert__', (inScope,)))

    @classmethod
    def union(cls, *args):
        allScopes, allDicts, commonkeys, uncommonkeys = \
            cls._process_args(*args)
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
        return cls(frozenset(outDict.items()), ('__union__', allScopes))

    @classmethod
    def difference(cls, *args):
        allScopes, allDicts, commonkeys, uncommonkeys = \
            cls._process_args(*args)
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
        return cls(frozenset(outDict.items()), ('__difference__', allScopes))

    @classmethod
    def intersection(cls, *args):
        allScopes, allDicts, commonkeys, uncommonkeys = \
            cls._process_args(*args)
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
        return cls(frozenset(outDict.items()), ('__intersection__', allScopes))

    @classmethod
    def symmetric(cls, *args):
        raise Exception("Not supported yet!")

    def __invert__(self): # ~
        return self.invert(self)
    def __or__(self, arg): # |
        return self.union(self, arg)
    def __lshift__(self, arg): # <<
        return self.difference(self, arg)
    def __rshift__(self, arg): # >>
        return self.difference(arg, self)
    def __and__(self, arg): # &
        return self.intersection(self, arg)
    def __xor__(self, arg): # ^
        return self.symmetric(self, arg)

class Reader:

    h5file = None

    def __init__(
            self,
            h5filename
            ):
        self.h5filename = h5filename
        self.file = partial(h5py.File, h5filename, 'r')

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

    # def view_attrs(self, scope = None):
    #     if scope is None:
    #         scope = self.full_scope()
    #     return self._view_attrs(scope)

    # @disk.h5filewrap
    # def _view_attrs(self, scope):
    #     outDict = dict()
    #     for superkey, scopeCounts in scope:
    #         builtGroup = self.h5file[superkey]
    #         for key in builtGroup.attrs:
    #             if not key in outDict:
    #                 outDict[key] = dict()
    #             keyval = builtGroup.attrs[key]
    #             if not keyval in outDict[key]:
    #                 outDict[key][keyval] = set()
    #             outDict[key][keyval].add((superkey, scopeCounts))
    #     for key in outDict:
    #         for subKey in outDict[key]:
    #             outDict[key][subKey] = Scope(outDict[key][subKey])
    #     return outDict

    # @staticmethod
    # def summary_of_dict(allDict):
    #     for key in sorted(allDict):
    #         print(key)
    #         for subKey in sorted(allDict[key]):
    #             print(subKey)
    #
    # @disk.h5filewrap
    # def sort_by_attr(self, key, scope = None):
    #     if scope is None:
    #         superkeys = self.h5file.keys()
    #     else:
    #         superkeys = [key for key, val in scope]
    #     outDict = dict()
    #     for superkey in superkeys:
    #         builtGroup = self.h5file[superkey]
    #         if key in builtGroup.attrs:
    #             keyval = builtGroup.attrs[key]
    #             if not keyval in outDict:
    #                 outDict[keyval] = set()
    #             newEntry = (superkey, '...')
    #             outDict[keyval].add(newEntry)
    #     for key in outDict:
    #         outDict[key] = Scope(outDict[key])
    #     return sorted(outDict.items())

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
        return outs

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

    context = __getitem__
