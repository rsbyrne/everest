import numpy as np
from collections import OrderedDict, namedtuple
from contextlib import contextmanager
from functools import wraps

from ..utilities import w_hash, get_hash
from ._producer import NullValueDetected, OutsNull
from ._voyager import Voyager
from ._stampable import Stampable, Stamper
from ._configurable import \
    Configurable, MutableConfigs, ImmutableConfigs, Config
from ._indexer import IndexerLoadRedundant
from .. import exceptions
from ..comparator import Comparator, Prop
from ..pyklet import Pyklet

class WandererException(exceptions.EverestException):
    pass

class StateException(exceptions.EverestException):
    pass
class ForbiddenSetItemOnState(StateException):
    pass
class RedundantState(StateException):
    pass

def _state_context_wrap(func):
    @wraps(func)
    def wrapper(state, *args, **kwargs):
        with state:
            pass
        return func(state, *args, **kwargs)
    return wrapper

class State(Stamper, ImmutableConfigs):
    def __init__(self, wanderer, slicer, _data = OrderedDict()):
        self.wanderer = wanderer
        if type(slicer) is tuple:
            slicer = slice(*slicer)
        start, stop, step = slicer.start, slicer.stop, slicer.step
        self.start = self._process_startpoint(start)
        self.stop = self._process_endpoint(stop)
        self.step = step
        if not self.step is None: raise exceptions.NotYetImplemented
        self._data = OrderedDict()
        self._data.name = self.start.hashID
        self._hashObjects = [self.wanderer, (self.start, self.stop, self.step)]
        statelets = OrderedDict([
            (k, Statelet(self, k))
                for k in self.wanderer.configs.keys()
            ])
        super().__init__(self,
            *[*self._hashObjects, self._data],
            contents = statelets,
            )
    def _process_startpoint(self, arg):
        return MutableConfigs(defaults = self.wanderer.configs, contents = arg)
        # if isinstance(arg, type(self)):
        # if isinstance(arg, Comparator):
        #     self._indexerStartpoint = False
        #     substart = self.wanderer.configs.copy()
        #     start = type(self)(self.wanderer, slice(substart, arg))
        # elif isinstance(arg, type(self)):
        #     if not arg.wanderer is self.wanderer:
        #         raise ValueError
        #     configs = None
        #     start = arg
        # elif arg is None:
        #     configs = self.wanderer.configs.copy()
        #     if self.wanderer._indexers_ispos:
        #         self._indexerStartpoint = True
        #         start = self._process_endpoint(self.indices[0])
        #     else:
        #         self._indexerStartpoint = False
        #         start = None
    def _process_endpoint(self, arg):
        if isinstance(arg, Comparator):
            self._indexerEndpoint = False
            return arg
        else:
            try:
                self._indexerEndpoint = True
                if arg is None:
                    if self.wanderer.initialised:
                        raise RedundantState
                    arg = self.wanderer.indices.count
                return self.wanderer._indexer_process_endpoint(arg)
            except IndexError:
                raise TypeError
    def __enter__(self):
        self._oldConfigs = self.wanderer.configs.copy()
        try:
            self._reloadVals = self.wanderer.outs.data.copy()
            self._reloadVals.name = self.wanderer.outs.name
        except NullValueDetected:
            self._reloadVals = None
        self.wanderer.set_configs(**self.start)
        if not len(self._data):
            if not self.wanderer.initialised:
                self.wanderer.initialise()
            while not self.stop:
                self.wanderer.iterate()
            self._data.update(self.wanderer.outs.data)
            self._indices = namedtuple(
                'IndexerHost',
                self.wanderer.indexerKeys)(
                    *[*self.wanderer.indexers]
                    )
        else:
            self.wanderer.load(self._data)
        return self
    def __exit__(self, *args):
        self.wanderer.set_configs(**self._oldConfigs)
        if self._reloadVals is None:
            self.wanderer.configure()
        else:
            try:
                self.wanderer.load(self._reloadVals)
            except IndexerLoadRedundant:
                pass
        del self._oldConfigs, self._reloadVals
    @property
    @_state_context_wrap
    def data(self):
        return self._data
    @property
    @_state_context_wrap
    def indices(self):
        return self._indices
    def _hashID(self):
        sliceStrs = [get_hash(o) for o in self._hashObjects[1]]
        return self._hashObjects[0].hashID + '[' + ':'.join(sliceStrs) + ']'

class Statelet(Config):
    def __init__(self, state, channel):
        self.state, self.channel = state, channel
        super().__init__(state, channel)
    def _hashID(self):
        return w_hash((self.state, self.channel))
    @property
    def data(self):
        return self.state.data[self.channel]
    @property
    def mutant(self):
        return self.state.wanderer.mutables[self.channel]
    @property
    def var(self):
        return self.mutant.var
    @contextmanager
    def temp_data(self):
        oldData = self.mutant.out()
        try:
            self.mutant.mutate(self.data)
            yield None
        finally:
            self.mutant.mutate(oldData)
    def _apply(self, toVar):
        with self.temp_data():
            super()._apply(toVar)

    # @property
    # def out(self):
    #     with self as out:
    #         return out

class Wanderer(Voyager, Configurable):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def _set_configs(self, *args, **kwargs):
        super()._set_configs(*args, **kwargs)
        self._nullify_indexers()

    def _initialise(self, *args, **kwargs):
        self.configure(silent = True)
        super()._initialise(*args, **kwargs)

    def __getitem__(self, arg):
        assert len(self.configs)
        if len(self.configs) == 1:
            return self._wanderer_get_single(arg)
        else:
            return self._wanderer_get_multi(arg)
    def _wanderer_get_single(self, arg):
        raise exceptions.NotYetImplemented
    def _wanderer_get_multi(self, arg):
        if type(arg) is str:
            if not arg in self.configs:
                raise ValueError
            return self[:][arg]
        else:
            if not type(arg) is slice:
                arg = slice(arg)
            try:
                return State(self, arg)
            except RedundantState:
                return ImmutableConfigs(contents = self.configs)

    def __setitem__(self, key, val):
        if isinstance(val, Wanderer):
            val = val[:]
        super().__setitem__(key, val)
        self.initialise(silent = True)

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configs.contentHash
