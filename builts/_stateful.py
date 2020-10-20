from collections import OrderedDict
from contextlib import contextmanager
import weakref

import numpy as np

from . import Built
from ..pyklet import Pyklet
from ..utilities import make_hash, w_hash, get_hash

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
from ..exceptions import EverestException
class StatefulException(BuiltException):
    pass
class StatefulMissingMethod(MissingMethod, StatefulException):
    pass
class StatefulMissingAttribute(MissingAttribute, StatefulException):
    pass
class StatefulMissingKwarg(MissingKwarg, StatefulException):
    pass
class StateletException(EverestException):
    pass
class StateletMissingMethod(EverestException):
    pass

class Statelet:
    def __init__(self, var, name):
        self._var, self._name = var, name
        super().__init__()
    def _hashID(self):
        return '_'.join([self.name, get_hash(self.var)])
    @property
    def var(self):
        return self._var
    @property
    def name(self):
        return self._name
    @property
    def varHash(self):
        return make_hash(self.out())
    def out(self):
        return self._out()
    def _out(self):
        if not isinstance(self.var, np.ndarray):
            raise StateletMissingMethod(
                "If var is not an array, provide a custom _out method."
                )
        return self.var.copy()
    @property
    def data(self):
        return self._data()
    def _data(self):
        if not isinstance(self.var, np.ndarray):
            raise StateletMissingMethod(
                "If var is not an array, provide a custom _data method."
                )
        return self.var
    def mutate(self, vals, indices = Ellipsis):
        return self._mutate(vals, indices)
    def _mutate(self, vals, indices = Ellipsis):
        self.data[indices] = vals
    def imitate(self, fromVar):
        if not type(fromVar) is type(self):
            raise TypeError
        self._imitate(fromVar)
    def _imitate(self, fromVar):
        self.mutate(fromVar.data)
    def __getitem__(self, arg):
        return self.out()[arg]
    def __setitem__(self, key, val):
        self.mutate(val, indices = key)

class State(OrderedDict):
    def __setitem__(self, key, arg):
        if not arg is None:
            if isinstance(arg, Statelet):
                if not key == arg.name:
                    raise ValueError
            else:
                raise TypeError
        super().__setitem__(key, arg)
    def __getitem__(self, key):
        return super().__getitem__(key)

class Stateful(Built):

    def __init__(self,
            _statefulKeys = None,
            **kwargs
            ):

        if _statefulKeys is None:
            raise StatefulMissingKwarg

        self.state = State([(k, None) for k in _statefulKeys])

        super().__init__(**kwargs)
