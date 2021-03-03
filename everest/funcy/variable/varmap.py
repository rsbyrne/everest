################################################################################

from collections.abc import MutableMapping

from . import _Map
from .variable import Variable as _Variable
from . import utilities as _utilities 

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
            return _utilities.construct_variable(v, name = k)
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
        for k, v in _utilities.ordered_unpack(self, key, val).items():
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
