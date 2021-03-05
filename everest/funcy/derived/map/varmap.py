################################################################################

from collections.abc import Sequence, Mapping, MutableMapping, Collection

from .map import Map as _Map
from . import _Variable, _construct_variable

from .exceptions import *

def ordered_unpack(keys, arg1, arg2):
    keys = tuple(keys)
    if arg1 is Ellipsis:
        seqChoice = range(len(keys))
        mapChoice = keys
    elif type(arg1) is str:
        seqChoice = [keys.index(arg1),]
        mapChoice = [arg1,]
    elif type(arg1) is int:
        seqChoice = [arg1,]
        mapChoice = [keys[arg1],]
    elif type(arg1) is tuple:
        if len(set([type(o) for o in arg1])) > 1:
            raise ValueError
        if type(arg1[0]) is str:
            seqFn = lambda arg: keys.index(arg)
            seqChoice = [seqFn(arg) for arg in arg1]
            mapChoice = arg1
        elif type(arg1[0] is int):
            mapFn = lambda arg: keys[arg]
            seqChoice = arg1
            mapChoice = [mapFn(arg) for arg in arg1]
        else:
            raise TypeError
    if type(arg2) is tuple:
        out = dict((keys[i], arg2[i]) for i in seqChoice)
    elif isinstance(arg2, Mapping):
        out = dict((k, arg2[k]) for k in mapChoice)
    else:
        out = dict((keys[i], arg2) for i in seqChoice)
    if arg1 is Ellipsis and type(arg2) is tuple:
        if not len(arg2) == len(out):
            raise IndexError("Not enough arguments.")
    return out

class VarMap(_Map, MutableMapping):
    def __init__(self, *args, **kwargs):
        values = tuple(self._proc_var(a) for a in args)
        keys = tuple(v.name for v in values)
        self.variables = values
        self.varNames = keys
        super().__init__(keys, values, **kwargs)
        self.defaults = dict(zip(keys, (v.value for v in values)))
    @staticmethod
    def _proc_var(arg):
        if type(arg) is tuple:
            print(arg)
            k, v = arg
            return _construct_variable(v, name = k)
        elif isinstance(arg, _Variable):
            return arg
        else:
            raise TypeError(type(arg))
    def __iter__(self):
        return iter(self.varNames)
    def __len__(self):
        return len(self.varNames)
    def _setitem(self, k, v):
        self.plain_get(k).value = v
    def __setitem__(self, key, val):
        for k, v in ordered_unpack(self, key, val).items():
            self.plain_get(k).value = v
    def __delitem__(self, k):
        self.plain_get(k).nullify()
    def nullify(self):
        for k in self:
            del self[k]
    def plain_get(self, k):
        return self.variables[self._keyind(k)]
    def reset(self):
        for k in self:
            self[k] = self.defaults[k]

class StackMap(VarMap):
    def __init__(self, keys, values, /, **kwargs):
        refined = list()
        for k, v in zip(keys, values):
            if isinstance(v, _Variable):
                if not v.name == k:
                    raise KeyError(v.name, k)
            else:
                v = _utilities.construct_variable(v, name = k, stack = True)
            refined.append(v)
        super().__init__(tuple(keys), tuple(refined), **kwargs)

################################################################################
