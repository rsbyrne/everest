from functools import wraps

from ._observable import Observable
from ._counter import Counter
from ._cycler import Cycler
from ._producer import LoadFail, _producer_update_outs
from ._stampable import Stampable
from ..comparator import Comparator, Prop

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
class VoyagerException(BuiltException):
    pass
class VoyagerMissingMethod(MissingMethod, VoyagerException):
    pass
class VoyagerMissingAttribute(MissingAttribute, VoyagerException):
    pass
class VoyagerMissingKwarg(MissingKwarg, VoyagerException):
    pass

def _voyager_initialise_if_necessary(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.initialised:
            self.initialise()
        return func(self, *args, **kwargs)
    return wrapper
def _voyager_uninitialise_if_necessary(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.initialised:
            self.uninitialise()
        return func(self, *args, **kwargs)
    return wrapper
def _voyager_changed_state(func):
    @wraps(func)
    @_producer_update_outs
    def wrapper(self, *args, **kwargs):
        pc = [*self.indices] if not self._indexers_isnull else True
        out = func(self, *args, **kwargs)
        nc = [*self.indices] if not self._indexers_isnull else True
        if nc != pc:
            self._voyager_changed_state_hook()
        return out
    return wrapper

class Voyager(Cycler, Counter, Stampable, Observable):

    def __init__(self,
            **kwargs
            ):

        self.baselines = dict()
        self._initialised = False

        super().__init__(**kwargs)

    def initialise(self):
        if self._indexers_isnull or not self._indexers_iszero:
            self._initialise()
            self._zero_indexers()
        assert self.initialised
    def _initialise(self):
        self._voyager_changed_state_hook()
        self._initialised = True
    def uninitialise(self):
        if not self._indexers_isnull:
            self._uninitialise()
            self._nullify_indexers()
        assert not self.initialised
    def _uninitialise(self):
        # self._voyager_changed_state_hook()
        self._initialised = False
    @property
    def initialised(self):
        assert self._initialised != self._indexers_isnull
        return self._initialised
    def reset(self):
        self.initialise()
    def _voyager_changed_state_hook(self):
        pass
        # self.advertise

    @_voyager_initialise_if_necessary
    def iterate(self, n = 1):
        for i in range(n):
            self._iterate()
    @_voyager_changed_state
    def _iterate(self):
        self.indices.count.value += 1
    def go(self, stop = False, step = 1, do = None):
        if type(step) is int:
            step = Comparator(Prop(self, 'indices', 'count'), step, op = 'mod')
        if do is None:
            do = lambda: None
        while not stop:
            self.iterate()
            while step:
                self.iterate()
            do()

    def _cycle(self):
        super()._cycle()
        self.iterate()

    def _load(self, *args, **kwargs):
        super()._load(*args, **kwargs)
        if self._indexers_isnull:
            self._uninitialise()
        elif self._indexers_iszero:
            self._initialise()
        else:
            assert self.initialised
            self._voyager_changed_state_hook()

        # Observable attributes:
        # self._activate_observation_mode_fns.append(
        #     self._voyager_activate_observation_mode_fn
        #     )
        # self._deactivate_observation_mode_fns.append(
        #     self._voyager_deactivate_observation_mode_fn
        #     )
    # def _voyager_activate_observation_mode_fn(self):
    #     temp = []
    #     for key in ('_outFns', '_producer_outkeys'):
    #         attr = getattr(self, key)
    #         temp.append([*attr])
    #         attr.clear()
    #     self._outFns.append(self._countoutFn)
    #     self._producer_outkeys.append(self._countsKeyFn)
    #     return temp
    # def _voyager_deactivate_observation_mode_fn(self, temp):
    #     for val, key in zip(temp, ('_outFns', '_producer_outkeys')):
    #         attr = getattr(self, key)
    #         attr.clear()
    #         attr.extend(val)
