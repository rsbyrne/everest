import h5py
import operator
import numpy as np
from functools import partial
from functools import reduce
from collections.abc import Set
from collections.abc import Hashable

from . import _specialnames

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

class Scope(Set, Hashable):

    __hash__ = Set._hash

    def _process_args(self, *args):
        if not all([type(arg) is Scope for arg in args]):
            raise TypeError
        args = list(args)
        args.append(self)
        allSets = [arg._set for arg in args]
        allDicts = [dict(subSet) for subSet in allSets]
        commonkeys = set.intersection(
            *[set(subDict) for subDict in allDicts]
            )
        return allDicts, commonkeys

    def union(self, *args):
        allDicts, commonkeys = self._process_args(*args)
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

    def keys(self):
        return set([key for key, val in self._set])

    def __add__(self, arg):
        return self.union(arg)

    def __mul__(self, arg):
        return self.intersection(arg)

    def intersection(self, *args):
        allDicts, commonkeys = self._process_args(*args)
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

    def __repr__(self):
        return "Scope({0})".format(list(self._set))

    def __new__(cls, iterable):
        selfobj = super(Scope, cls).__new__(Scope)
        cleaned_iterable = _process_scope_inputs(iterable)
        selfobj._set = frozenset(cleaned_iterable)
        return selfobj

    def __getattr__(self, attr):
        return getattr(self._set, attr)

    def __contains__(self, item):
        return item in self._set

    def __len__(self):
        return len(self._set)

    def __iter__(self):
        return iter(self._set)

class Fetch:

    operations = operator.__dict__
    operations[None] = lambda *args: True

    def __init__(
            self,
            *args,
            operation = None
            ):
        self.args = args
        self.operation = operation

    def __call__(self, context = None):
        if context is None:
            context = lambda *inp: inp
        try:
            args = context(*self.args)
            return self.operations[self.operation](*args)
        except KeyError:
            return False

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

def _readwrap(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        h5filename = self.h5filename
        with h5py.File(h5filename, 'r') as h5file:
            self.h5file = h5file
            outputs = func(*args, **kwargs)
        return outputs
    return wrapper

class Reader:
    def __init__(
            self,
            h5filename
            ):
        self.h5file = None
        self.h5filename = h5filename
        self.file = partial(h5py.File, h5filename, 'r')

    @_readwrap
    def full_scope(self):
        scopelets = set()
        for superkey in self.h5file:
            scopelets.add((superkey, '...'))
        return Scope(scopelets)

    @_readwrap
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
                # import time
                # prevtime = time.clock()
                thisCountsDataset = thisGroup[_specialnames.COUNTS_FLAG]
                maskFn = lambda val: val in scopeCounts
                mask = np.vectorize(maskFn)(thisCountsDataset[...])
                # print("To make the mask array: ", time.clock() - prevtime)
                # prevtime = time.clock()
                arr = thisTargetDataset[mask]
                # print("To apply the mask to the array: ", time.clock() - prevtime)
            arrList.append(arr)
        allArr = np.concatenate(arrList)
        return allArr

    def view_attrs(self, scope = None):
        if scope is None:
            scope = self.full_scope()
        return self._view_attrs(scope)

    @_readwrap
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

    @_readwrap
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
        if type(inp) is tuple:
            allouts = [self.__getitem__(subInp) for subInp in inp]
            return allouts[0].intersection(*allouts[1:])
        if type(inp) is Fetch:
            return self._get_fetch(inp)
        if type(inp) is Scope:
            raise Exception("That behaviour not supported yet")
        raise TypeError

    def _process_out(self, out):
        if type(out) is str:
            return out
        if type(out) is h5py.Dataset:
            return out[...]
        return eval(str(out))

    def _context(self, superkey, *args):
        args = list(args)
        key = args.pop(0)
        try: out = self.h5file[superkey].attrs[key]
        except: out = self.h5file[superkey][key]
        out = self._process_out(out)
        return (out, *args)

    @_readwrap
    def _get_fetch(self, fetch):
        outs = set()
        for superkey in self.h5file:
            context = partial(
                self._context,
                superkey
                )
            result = fetch(context)
            indices = None
            if type(result) is bool:
                if fetch(context):
                    indices = '...'
            elif type(result) is np.ndarray:
                if np.all(result):
                    indices = '...'
                elif np.any(result):
                    indices = tuple(
                        self.h5file\
                            [superkey] \
                            [_specialnames.COUNTS_FLAG] \
                            [result]
                        )
            if not indices is None:
                outs.add((superkey, indices))
        outs = Scope(outs)
        return outs
