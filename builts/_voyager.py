import numpy as np
from functools import wraps

from .. import disk
from ._observable import Observable
from ._counter import Counter
from ._cycler import Cycler
from ._producer import Producer, LoadFail
from ._state import State
from .. import exceptions
from .. import mpi
from ..value import Value
from ..weaklist import WeakList

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
class VoyagerException(BuiltException):
    pass
class VoyagerMissingMethod(MissingMethod, VoyagerException):
    pass
class VoyagerMissingAttribute(MissingAttribute, VoyagerException):
    pass
class VoyagerMissingKwarg(MissingKwarg, VoyagerException):
    pass

def _voyager_must_be_initialised(func):
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

class Voyager(Cycler, Observable, Counter):

    def __init__(
            self,
            _voyager_initialise = True,
            **kwargs
            ):

        self.baselines = dict()

        super().__init__(**kwargs)

        if _voyager_initialise:
            self.initialise()

    def _outkeys(self):
        for o in super()._outkeys(): yield o
        for o in self._voyager_outkeys(): yield o
    def _voyager_outkeys(self):
        raise VoyagerMissingMethod
    def _out(self):
        for o in super()._out(): yield o
        for o in self._voyager_out(): yield o
    @_voyager_initialised
    def _voyager_out(self):
        raise VoyagerMissingMethod

    @property
    def initialised(self):
        return all([*self._initialised()])
    def _initialised(self):
        yield True
    @_voyager_changed_state
    def initialise(self, *args, **kwargs):
        if self.count == 0:
            pass
        else:
            try:
                self.load(0)
            except LoadFail:
                self._initialise(*args, **kwargs)
            self.count.value = 0
            self.initialised = True
    def reset(self):
        self.initialise()
    def _voyager_changed_state_hook(self):
        # self.advertise
        pass

    @_voyager_changed_state
    def _single_iterate(self):
        self.count += 1
        self._iterate()
    @_voyager_initialised
    def iterate(self, n = 1):
        for i in range(n):
            self._single_iterate()
            # mpi.message('.')
    @_voyager_initialised
    def go(self, stop = False):
        while not stop:
            self.iterate()

    def _cycle(self):
        super()._cycle()
        self.iterate()

    @_voyager_initialised
    def _save(self):
        self.writer.add_dict(self.baselines, 'baselines')
        super()._save()

    @_voyager_changed_state
    def _load_process(self, outs):
        outs = super()._load_process(outs)
        ks = self._voyager_outkeys()
        self._voyager_load_update(dict(zip(ks, [outs.pop(k) for k in ks])))
        return outs
    def _voyager_load_update(self, outs):
        raise VoyagerMissingMethod

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

    #
    # def load(self, arg, **kwargs):
    #     try:
    #         if type(arg) is Value:
    #             self.load(arg.plain)
    #         elif type(arg) is str:
    #             if arg == 'max':
    #                 self.load(max(self.counts))
    #             elif arg == 'min':
    #                 self.load(min(self.counts))
    #             else:
    #                 raise ValueError("String input must be 'max' or 'min'.")
    #         elif type(arg) is int:
    #             self._load_count(arg, **kwargs)
    #         elif type(arg) is float:
    #             self._load_chron(arg, **kwargs)
    #         elif type(arg) is list:
    #             self._load_outs(arg, **kwargs)
    #         elif isinstance(arg, State):
    #             self._load_state(arg, **kwargs)
    #         else:
    #             try:
    #                 num = float(arg)
    #                 if num % 1.:
    #                     self.load(float(arg))
    #                 else:
    #                     self.load(int(arg))
    #             except ValueError:
    #                 raise TypeError("Unacceptable type", type(arg))
    #         self.initialised = True
    #     except (LoadDiskFail, LoadStampFail, LoadStoredFail, LoadFail):
    #         raise LoadFail
    #
    # @_voyager_changed_state
    # def _load_process_outs(self, outs):
    #     outsDict = dict(zip(self.outkeys, self.outs))
    #     self.count.value = outsDict.pop(self._countsKey)
    #     self._load_process(outsDict)
    #
    # def _load_process_state(self, state, earliest = True, _updated = False):
    #     if earliest: stamps = self.stamps[::-1]
    #     else: stamps = self.stamps
    #     try:
    #         count = dict(stamps)[state.hashID]
    #         self._load_count(count)
    #     except KeyError:
    #         if _updated:
    #             raise LoadStampFail
    #         elif self.anchored:
    #             self._stampable_update()
    #             self._load_state(state, earliest = earliest, _updated = True)
    #         else:
    #             raise LoadStampFail
    #
    # def _load_process_chron(self, inChron):
    #     if not hasattr(self, 'chron'):
    #         raise Exception("Voyager has no provided chron.")
    #     if inChron < 0.:
    #         inChron += self.chron
    #     counts, chrons = [], []
    #     if self.anchored:
    #         counts.extend(self.readouts['count'])
    #         chrons.extend(self.readouts['chron'])
    #     dataDict = self.dataDict
    #     if len(dataDict):
    #         counts.extend(dataDict['count'])
    #         chrons.extend(dataDict['chron'])
    #     counts.sort()
    #     chrons.sort()
    #     inCount = None
    #     for chron, count in zip(chrons, counts):
    #         if chron >= inChron:
    #             inCount = count
    #             break
    #     if inCount is None:
    #         raise LoadFail
    #     else:
    #         self._load_count(inCount)
    #
    # def _load_process_count(self, count):
    #     if count < 0:
    #         if self.initialised:
    #             count += self.count
    #         else:
    #             pass
    #     elif count == self.count:
    #         pass
    #     else:
    #         if count in self.counts_stored:
    #             loadOuts = self.stored[self.counts_stored.index(count)]
    #         elif count in self.counts_disk:
    #             index = self.counts_disk.index(count)
    #             loadOuts = [
    #                 self.readouts[key][self.counts_disk.index(count)]
    #                     for key in self.outkeys
    #                     ]
    #         else:
    #             raise LoadFail
    #         loadDict = dict(zip(self.dataKeys, [data[index] for data in datas]))
    #         self.count.value = count
    #         self._load_process(loadDict)
