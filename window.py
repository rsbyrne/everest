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

    _unaryOps = {
        None,
        '__invert__',
        '__neg__'
        }

    def __init__(
            self,
            *args,
            operation = None
            ):
        unary = len(args) == 1
        assert unary == (operation in self._unaryOps)
        assert (not unary) == (not operation in self._unaryOps)
        if unary:
            self.arg = args[0]
        self.args = args
        self.operation = operation
        self.unary = unary

    @classmethod
    def _operate(cls, *args, operation = None, context = None):
        operands = []
        for arg in args:
            if type(arg) is Fetch:
                opVals = arg(context)
            else:
                opVals = np.array(arg)
            operands.append(opVals)
        operation = operator.__dict__[operation]
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
            out = context(self.arg)
        else:
            out = self._operate(
                *self.args,
                operation = self.operation,
                context = context
                )
        return out

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
        raise NotImplmentedError
        return Fetch(*args, operation = 'union')
    def __lshift__(*args): # |
        raise NotImplmentedError
        return Fetch(*args, operation = 'difference')
    def __and__(*args): # &
        raise NotImplmentedError
        return Fetch(*args, operation = 'intersection')
    def __xor__(*args): # ^
        raise NotImplmentedError
        return Fetch(*args, operation = 'symmetric')

    # def __call__(self, context):
    #     if context is None:
    #         context = lambda *inp: inp
    #     try:
    #         args = context(*self.args)
    #         if len(args) == 0:
    #             output = np.array(True)
    #         else:
    #             args = [np.array(arg) for arg in args]
    #             output = np.array(
    #                 self.operations[self.operation](*args)
    #                 ).flatten()
    #     except KeyError:
    #         output = np.array(False)
    #     if 'invert' in self.options:
    #         return ~output
    #     else:
    #         return output

    # def __lt__(self, *args):
    #     return Fetch(self, *args, operation = 'lt')
    # def __le__(self, *args):
    #     return Fetch(self *args, operation = 'le')
    # def __eq__(self, *args):
    #     return Fetch(*self.args, *args, operation = 'eq')
    # def __ne__(self, *args):
    #     return Fetch(*self.args, *args, operation = 'ne')
    # def __ge__(self, *args):
    #     return Fetch(*self.args, *args, operation = 'ge')
    # def __gt__(self, *args):
    #     return Fetch(*self.args, *args, operation = 'gt')
    # def __invert__(self):
    #     return Fetch(*self.args, operation = self.operation,
    #         options = ['invert']
    #         )
    # def __add__(self, arg):
    #     return Pending(self, arg, function = Scope.union)
    # def __sub__(self, arg):
    #     return Pending(self, arg, function = Scope.difference)
    # def __mul__(self, arg):
    #     return Pending(self, arg, function = Scope.intersection)
    # def __div__(self, arg):
    #     return Pending(self, arg, function = Scope.symmetric)
#
# class Pending:
#     def __init__(self, *args, function = None):
#         self.args = args
#         self.function = function
#     def __call__(self, getscopesFn):
#         scopes = []
#         for arg in self.args:
#             if type(arg) is Scope:
#                 scope = arg
#             else:
#                 scope = getscopesFn(arg)
#             scopes.append(scope)
#         outScope = self.function(*scopes)
#         return outScope
#     def __add__(self, arg):
#         return Pending(self, arg, function = Scope.union)
#     def __sub__(self, arg):
#         return Pending(self, arg, function = Scope.difference)
#     def __mul__(self, arg):
#         return Pending(self, arg, function = Scope.intersection)
#     def __div__(self, arg):
#         return Pending(self, arg, function = Scope.symmetric)

class Scope(Set, Hashable):

    __hash__ = Set._hash

    def __new__(cls, inFetch, context):
        selfobj = super(Scope, cls).__new__(Scope)
        unclean_iterable = cls._process_fetch(inFetch, context)
        cleaned_iterable = cls._process_iterable(unclean_iterable)
        selfobj._set = frozenset(cleaned_iterable)
        selfobj.fetch = inFetch
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
                    indices = tuple(indices_)
            except:
                raise TypeError
            if not indices is None:
                outs.add((superkey, indices))
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

    def __add__(self, arg):
        return self._operation(self, arg, opFn = self.union)
    def __sub__(self, arg):
        return self._operation(self, arg, opFn = self.difference)
    def __mul__(self, arg):
        return self._operation(self, arg, opFn = self.intersection)
    def __div__(self, arg):
        return self._operation(self, arg, opFn = self.symmetric)

    def __or__(self, arg):
        return self._operation(self, arg, opFn = self.union)
    def __lshift__(self, arg):
        return self._operation(self, arg, opFn = self.difference)
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

    def _gettuple(self, inp):
        return [self.__getitem__(subInp) for subInp in inp]

    @disk.h5filewrap
    def _getstr(self, key):
        sought = self._seek(key, self.h5file)
        resolved = self._seekresolve(sought)
        if type(resolved) is dict:
            out = utilities.flatten(resolved, sep = '/')
        else:
            out = resolved
        return out

    @classmethod
    def _seek(cls, key, searchArea):
        # expects h5filewrap
        splitkey = key.split('/')
        if splitkey[-1] == '*':
            key = '/'.join(splitkey[:-1])
        if splitkey[0] == '*':
            if hasattr(searchArea, 'keys'):
                remKey = '/'.join(splitkey[1:])
                outDict = dict()
                for subKey, subItem in searchArea.items():
                    sought = cls._seek(remKey, subItem)
                    if not sought is None:
                        outDict[subKey] = sought
                if len(outDict) > 0:
                    out = outDict
                else:
                    out = None
            else:
                out = None
        elif len(key) > 0:
            pathkey = '/'.join(splitkey[:-1])
            attrkey = splitkey[-1]
            if hasattr(searchArea, 'keys'):
                try:
                    if key in searchArea:
                        out = searchArea[key]
                    elif key in searchArea.attrs:
                        out = searchArea.attrs[key]
                    else:
                        out = searchArea[pathkey].attrs[attrkey]
                except (KeyError, ValueError):
                    out = None
            else:
                try:
                    if key in searchArea.attrs:
                        out = searchArea.attrs[key]
                    else:
                        out = searchArea[pathkey].attrs[attrkey]
                except (KeyError, ValueError):
                    out = None
        else:
            out = searchArea
            # out = None
        if splitkey[-1] == '*':
            if not out is None and not type(out) is dict:
                newOut = list()
                if hasattr(out, 'keys'):
                    newOut.extend(out.keys())
                if hasattr(out, 'attrs'):
                    newOut.extend(out.attrs.keys())
                if len(newOut) > 0:
                    out = newOut
        return out

    @classmethod
    def _seekresolve(cls, toResolve):
        if type(toResolve) is dict:
            out = dict()
            for key, val in toResolve.items():
                out[key] = cls._seekresolve(val)
        elif type(toResolve) == h5py._hl.group.Group:
            out = toResolve.name
        elif type(toResolve) == h5py._hl.dataset.Dataset:
            out = np.array(toResolve)
        elif isinstance(toResolve, np.generic):
            out = np.asscalar(toResolve)
        else:
            out = toResolve
        return out

    def _getfetch(self, fetch):
        return Scope(fetch, self.__getitem__)

    def _getslice(self, inp):
        return self.pull(inp.start, inp.stop)

    def _getellipsis(self, inp):
        pass

    _getmethods = {
        tuple: _gettuple,
        str: _getstr,
        Fetch: _getfetch,
        slice: _getslice,
        Ellipsis: _getellipsis
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
