import numpy as np
from functools import wraps

from .. import disk
from ._observable import Observable
from ._counter import Counter
from ._cycler import Cycler
from ._producer import Producer
from ._stampable import Stampable
from ._state import State
from ._unique import Unique
from ..exceptions import EverestException
from .. import mpi
from ..value import Value
from ..weaklist import WeakList

class LoadFail(EverestException):
    pass
class LoadDiskFail(EverestException):
    pass
class LoadStoredFail(EverestException):
    pass
class LoadStampFail(EverestException):
    pass

class Bounce:
    def __init__(self, iterator, arg = 0):
        self.iterator = iterator
        self.arg = arg
    def __enter__(self):
        self.returnStep = self.iterator.count.value
        self.iterator.store()
        if self.arg == 0: self.iterator.reset()
        else: self.iterator.load(self.arg)
    def __exit__(self, *args):
        self.iterator.load(self.returnStep)

def _initialised(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.initialised:
            self.initialise()
        return func(self, *args, **kwargs)
    return wrapper

def _changed_state(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        prevCount = self.count.value
        out = func(self, *args, **kwargs)
        if not self.count.value == prevCount:
            for fn in self._changed_state_fns:
                fn()
        return out
    return wrapper

class Voyager(Counter, Cycler, Stampable, Unique, Observable):

    def __init__(
            self,
            _voyager_initialise = True,
            **kwargs
            ):

        # Expects:
        # self._initialise
        # self._iterate
        # self._voyager_out
        # self._voyager_outkeys
        # self._load

        self.initialised = False

        self._changed_state_fns = WeakList()

        self.baselines = dict()

        super().__init__(**kwargs)

        # Prompter attributes:
        self._changed_state_fns.append(self.advertise)
        self._producer_outkeys.append(self._voyager_outkeys)

        # Producer attributes:
        self._outFns.append(self._voyager_master_out_fn)
        self._pre_save_fns.append(self._voyager_pre_save_fn)

        # Cycler attributes:
        self._cycle_fns.append(self.iterate)

        # Observable attributes:
        self._activate_observation_mode_fns.append(
            self._voyager_activate_observation_mode_fn
            )
        self._deactivate_observation_mode_fns.append(
            self._voyager_deactivate_observation_mode_fn
            )

        if _voyager_initialise:
            self.initialise()

                # oldOutFns = [*subject._outFns]
                # oldOutKeys = [*subject._producer_outkeys]
                # subject._outFns.clear()
                # subject._producer_outkeys.clear()
                # if isinstance(subject, Counter):
                #     subject._outFns.append([subject.])
                # subject._outFns.remove(subject.)

    def _voyager_activate_observation_mode_fn(self):
        temp = []
        for key in ('_outFns', '_producer_outkeys'):
            attr = getattr(self, key)
            temp.append([*attr])
            attr.clear()
        self._outFns.append(self._countoutFn)
        self._producer_outkeys.append(self._countsKeyFn)
        return temp
    def _voyager_deactivate_observation_mode_fn(self, temp):
        for val, key in zip(temp, ('_outFns', '_producer_outkeys')):
            attr = getattr(self, key)
            attr.clear()
            attr.extend(val)

    @_initialised
    def _voyager_pre_save_fn(self):
        self.writer.add_dict(self.baselines, 'baselines')

    @property
    def _voyager_outkeys(self):
        # Expects to be overridden.
        return []

    @property
    def dataKeys(self):
        return [
            key for key in self.outkeys if not key == self._countsKey
            ]

    @_initialised
    def _voyager_master_out_fn(self):
        if hasattr(self, '_voyager_out'):
            for item in self._voyager_out():
                yield item
        else:
            pass

    @_changed_state
    def initialise(self, *args, **kwargs):
        try:
            self.load(0)
        except LoadFail:
            self._initialise(*args, **kwargs)
        self.count.value = 0
        self.initialised = True

    @_initialised
    def out(self):
        # Wraps parent (Producer) method:
        return super().out()

    def reset(self):
        self.initialise()

    @_changed_state
    def _single_iterate(self):
        self.count += 1
        self._iterate()

    @_initialised
    def iterate(self, n = 1):
        for i in range(n):
            self._single_iterate()
            # mpi.message('.')

    @_initialised
    def go(self, stop = False):
        while not stop:
            self.iterate()

    @_changed_state
    def load(self, arg, **kwargs):
        try:
            if type(arg) is Value:
                self.load(arg.plain)
            elif type(arg) is str:
                if arg == 'max':
                    self.load(max(self.counts))
                elif arg == 'min':
                    self.load(min(self.counts))
                else:
                    raise ValueError("String input must be 'max' or 'min'.")
            elif type(arg) is int:
                self._load_count(arg, **kwargs)
            elif type(arg) is float:
                self._load_chron(arg, **kwargs)
            elif isinstance(arg, State):
                self._load_state(arg, **kwargs)
            else:
                try:
                    num = float(arg)
                    if num % 1.:
                        self.load(float(arg))
                    else:
                        self.load(int(arg))
                except ValueError:
                    raise TypeError("Unacceptable type", type(arg))
            self.initialised = True
        except (LoadDiskFail, LoadStampFail, LoadStoredFail, LoadFail):
            raise LoadFail

    def _load_state(self, state, earliest = True, _updated = False):
        if earliest: stamps = self.stamps[::-1]
        else: stamps = self.stamps
        try:
            count = dict(stamps)[state.hashID]
            self._load_count(count)
        except KeyError:
            if _updated:
                raise LoadStampFail
            elif self.anchored:
                self._stampable_update()
                self._load_state(state, earliest = earliest, _updated = True)
            else:
                raise LoadStampFail

    def _load_chron(self, inChron):
        if not hasattr(self, 'chron'):
            raise Exception("Voyager has no provided chron.")
        if inChron < 0.:
            inChron += self.chron
        counts, chrons = [], []
        if self.anchored:
            counts.extend(self.readouts['count'])
            chrons.extend(self.readouts['chron'])
        dataDict = self.dataDict
        if len(dataDict):
            counts.extend(dataDict['count'])
            chrons.extend(dataDict['chron'])
        counts.sort()
        chrons.sort()
        inCount = None
        for chron, count in zip(chrons, counts):
            if chron >= inChron:
                inCount = count
                break
        if inCount is None:
            raise LoadFail
        else:
            self._load_count(inCount)

    def _load_count(self, count):
        if count < 0:
            if self.initialised:
                count += self.count
            else:
                pass
        elif count == self.count:
            pass
        else:
            if count in self.counts_stored:
                index = self.counts_stored.index(count)
                datas = [self.dataDict[key] for key in self.dataKeys]
            elif count in self.counts_disk:
                index = self.counts_disk.index(count)
                datas = [self.readouts[key] for key in self.dataKeys]
            else:
                raise LoadFail
            loadDict = dict(zip(self.dataKeys, [data[index] for data in datas]))
            self.count.value = count
            self._load(loadDict)

    def _load(self, loadDict):
        # expects to be overridden:
        assert not len(loadDict), "No _load fn provided!"

    def bounce(self, count):
        return Bounce(self, count)
