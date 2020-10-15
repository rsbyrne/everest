from functools import wraps

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

def _voyager_initialise_if_necessary(post = False):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if post:
                cond = self.initialised or self.postinitialised
            else:
                cond = self.initialised
            if not cond:
                self.initialise()
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
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

class Voyager(Cycler, Counter, Stampable):

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
    @property
    def postinitialised(self):
        return self._indexers_ispos
    def reset(self, silent = True):
        self.initialise(silent = silent)
    @_producer_update_outs
    def _voyager_changed_state_hook(self):
        pass

    @_voyager_initialise_if_necessary(post = True)
    def iterate(self, n = 1, silent = True):
        for i in range(n):
            self._iterate()
    @_voyager_changed_state
    def _iterate(self):
        self.indices.count.value += 1

    @_voyager_initialise_if_necessary(post = True)
    def go(self, stop):
        if type(stop) is bool:
            self._go()
            return None
        try:
            self.load(stop)
        except LoadFail:
            if not isinstance(stop, Comparator):
                stop = self._indexer_process_endpoint(stop, close = False)
            if self._indexers_isnull:
                self.initialise()
            slots = stop.slots
            if slots == 1:
                boolean = stop.close(self)
            elif slots == 0:
                boolean = stop
            else:
                raise ValueError("Too many slots on comparator.")
            self.reset()
            if boolean:
                raise Exception("Condition already met.")
            self._go(boolean)
    def _go(self, stop = False):
        while not stop:
            self.iterate()

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
