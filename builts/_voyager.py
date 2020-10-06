from functools import wraps

from ._observable import Observable
from ._counter import Counter
from ._cycler import Cycler
from ._producer import LoadFail
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
def _voyager_changed_state(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        prevCount = self.count.value
        out = func(self, *args, **kwargs)
        if not self.count.value == prevCount:
            self._voyager_changed_state_hook()
        return out
    return wrapper

class Voyager(Cycler, Counter, Stampable, Observable):

    def __init__(self,
            **kwargs
            ):

        self.baselines = dict()

        super().__init__(**kwargs)

    @_voyager_changed_state
    def initialise(self, *args, **kwargs):
        if self.count == 0:
            pass
        else:
            try:
                self.load(0)
            except LoadFail:
                self._initialise(*args, **kwargs)
        self.initialised = True
    def _initialise(self, *args, **kwargs):
        self.count.value = 0
    def reset(self):
        self.initialise()
    def _voyager_changed_state_hook(self):
        # self.advertise
        pass

    @_voyager_initialise_if_necessary
    def iterate(self, n = 1):
        for i in range(n):
            self._iterate()
    @_voyager_changed_state
    def _iterate(self):
        self.count += 1
    def go(self, stop = False, step = 1, do = None):
        if type(step) is int:
            step = Comparator(Prop(self, 'count'), step, op = 'mod')
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
