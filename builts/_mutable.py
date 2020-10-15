from collections import OrderedDict
from contextlib import contextmanager

from . import Built
from ..pyklet import Pyklet
from ..utilities import make_hash, w_hash, get_hash
from ..prop import Prop

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
from ..exceptions import EverestException
class MutableException(BuiltException):
    pass
class MutableMissingMethod(MissingMethod, MutableException):
    pass
class MutableMissingAttribute(MissingAttribute, MutableException):
    pass
class MutableMissingKwarg(MissingKwarg, MutableException):
    pass
class MutantException(EverestException):
    pass
class MutantMissingMethod(EverestException):
    pass

class Mutant(Pyklet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def _hashID(self):
        return '_'.join([self.name, get_hash(self.var)])
    @property
    def var(self):
        return self._var()
    def _var(self):
        raise MutantMissingMethod
    @property
    def name(self):
        return self._name()
    def _name(self):
        raise MutantMissingMethod
    @property
    def varHash(self):
        return make_hash(self.out())
    def out(self):
        return self._out()
    def _out(self):
        raise MutantMissingMethod
    @property
    def data(self):
        return self._data()
    def _data(self):
        raise MutantMissingMethod
    def mutate(self, vals, indices = Ellipsis):
        return self._mutate(vals, indices)
    def _mutate(self, vals, indices = Ellipsis):
        self.data[indices] = vals
    def imitate(self, fromVar):
        if not type(fromVar) is type(self):
            raise TypeError
        self._imitate(fromVar)
    def _imitate(self, fromVar):
        self.data[...] = fromVar.data
    def __getitem__(self, arg):
        return self.out()[arg]
    def __setitem__(self, key, val):
        self.mutate(val, indices = key)

class Mutables(OrderedDict):
    def __setitem__(self, key, arg):
        if not arg is None:
            if isinstance(arg, Mutant):
                if not key == arg.name:
                    raise ValueError
            else:
                raise TypeError
        super().__setitem__(key, arg)

class Mutable(Built):

    def __init__(self,
            _mutableKeys = None,
            **kwargs
            ):

        if _mutableKeys is None:
            raise MutableMissingKwarg

        self.mutables = Mutables([(k, None) for k in _mutableKeys])

        super().__init__(**kwargs)
