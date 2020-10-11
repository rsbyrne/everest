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
class VoyagerAlreadyInitialised(VoyagerException):
    pass
class VoyagerNotInitialised(VoyagerException):
    pass

def _voyager_initialise_if_necessary(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.initialised:
            self.initialise()
        return func(self, *args, **kwargs)
    return wrapper
def _voyager_changed_state(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        pc = [i.value for i in self.indices]
        out = func(self, *args, **kwargs)
        nc = [i.value for i in self.indices]
        if nc != pc:
            self._voyager_changed_state_hook()
        return out
    return wrapper

class Voyager(Cycler, Counter, Stampable, Observable):

    def __init__(self,
            **kwargs
            ):

        self.baselines = dict()

        super().__init__(**kwargs)

    def initialise(self, silent = False):
        if self.initialised:
            if silent:
                pass
            else:
                raise VoyagerAlreadyInitialised
        else:
            self._initialise()
            assert self.initialised
    def _initialise(self):
        self._zero_indexers()
        self._voyager_changed_state_hook()
    @property
    def initialised(self):
        return self._indexers_iszero
    def reset(self):
        self.initialise()
    @_producer_update_outs
    def _voyager_changed_state_hook(self):
        pass

    def iterate(self, n = 1):
        if self._indexers_isnull:
            raise VoyagerNotInitialised
        for i in range(n):
            self._iterate()
    @_voyager_changed_state
    def _iterate(self):
        self.indices.count.value += 1

    def _cycle(self):
        super()._cycle()
        self.iterate()

    @_voyager_changed_state
    def _load(self, *args, **kwargs):
        super()._load(*args, **kwargs)

    # @_voyager_initialise_if_necessary
    # def go(self, stop = False, step = 1, do = None):
    #     print(self.indices)
    #     print([*self.indices][0].null)
    #     if type(step) is int:
    #         if step == 1:
    #             step = False
    #         else:
    #             step = Comparator(
    #                 Prop(self, 'indices', 'count'), step, op = 'mod'
    #                 )
    #     if do is None:
    #         do = lambda: None
    #     while not stop:
    #         self.iterate()
    #         while step:
    #             self.iterate()
    #         do()


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
