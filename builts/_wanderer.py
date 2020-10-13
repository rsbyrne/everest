import numpy as np
from collections import OrderedDict, namedtuple
from contextlib import contextmanager
from functools import wraps
import warnings
import weakref

from ..utilities import w_hash, get_hash
from ._producer import NullValueDetected, OutsNull
from ._voyager import Voyager
from ._stampable import Stampable, Stamper
from ._configurable import \
    Configurable, MutableConfigs, ImmutableConfigs, Configs, Config, \
    CannotProcessConfigs
from ._configurator import Configurator
from ._indexer import IndexerLoadRedundant, IndexerLoadFail
from .. import exceptions
from ..comparator import Comparator, Prop
from ..pyklet import Pyklet
from ..utilities import is_numeric

class WandererException(exceptions.EverestException):
    pass

class StateException(exceptions.EverestException):
    pass
class RedundantState(StateException):
    pass

def _state_context_wrap(func):
    @wraps(func)
    def wrapper(state, *args, **kwargs):
        if not state._computed:
            state._compute()
        return func(state, *args, **kwargs)
    return wrapper

class State(Stamper, ImmutableConfigs):
    _premade = weakref.WeakValueDictionary()
    @classmethod
    def get_state(cls, wanderer, slicer):
        obj = cls(wanderer, slicer)
        try:
            obj = cls._premade[obj.contentHash]
        except KeyError:
            cls._premade[obj.contentHash] = obj
        return obj
    def __init__(self, wanderer, slicer):
        self.start, self.stop = get_start_stop(wanderer, slicer)
        self.wanderer = wanderer
        self._stateArgs = (wanderer, (self.start, self.stop))
        statelets = OrderedDict([
            (k, Statelet(self, k))
                for k in self.wanderer.configs.keys()
            ])
        statelets = self.wanderer.process_configs(statelets)
        self._computed = False
        super().__init__(self,
            contents = statelets,
            )
    def _pickle(self):
        return self._stateArgs, OrderedDict()
    def _compute(self):
        assert not self._computed
        self.localWanderer = wanderer.copy()
        self.localWanderer.gofrom(self.start, self.stop)
        self._data = self.localWanderer.outs.data.copy()
        self._data.name = self.localWanderer.outputSubKey
        iks = self.localWanderer.indexerKeys
        self._indices = namedtuple('IndexerHost', iks)(
            *[i.value for i in self.localWanderer.indexers]
            )
        self._computed = True
    @property
    @_state_context_wrap
    def data(self):
        return self._data
    @property
    @_state_context_wrap
    def indices(self):
        return self._indices
    @property
    @_state_context_wrap
    def mutables(self):
        return self.localWanderer.mutables

class Statelet(Config):
    def __init__(self, state, channel):
        self.state, self.channel = state, channel
        self._stateletHashID = self._make_hashID(
            self.channel,
            *self.state._stateArgs
            )
        super().__init__(content = (self.channel, self.state._stateArgs))
    @staticmethod
    def _make_hashID(channel, wanderer, sliceTup):
        if wanderer.configs[channel] is Ellipsis:
            return w_hash(str(Ellipsis))
        else:
            return w_hash((
                channel,
                wanderer.hashID,
                *[o.contentHash if hasattr(o, 'contentHash') else get_hash(o)
                    for o in sliceTup]
                ))
    def _hashID(self):
        return self._stateletHashID
    def _pickle(self):
        return (self.state, self.channel), OrderedDict()
    @property
    def data(self):
        return self.state.data[self.channel]
    @property
    def mutant(self):
        return self.state.mutables[self.channel]
    @property
    def var(self):
        return self.mutant.var
    def _apply(self, toVar):
        assert not self.state.localWanderer is toVar.host
        super()._apply(toVar)

def get_start_stop(wanderer, slicer):
    if type(slicer) is tuple:
        slicer = slice(*slicer)
    start, stop, step = slicer.start, slicer.stop, slicer.step
    if not step is None:
        raise ValueError("Cannot specify step for state.")
    stop = wanderer.indices.count.value if stop is None else stop
    if is_numeric(stop):
        if not start is None:
            warnings.warn("Specified start point is redundant; ignoring.")
        start = ImmutableConfigs(contents = wanderer.configs)
        stop = wanderer._indexer_process_endpoint(stop)
    elif isinstance(stop, Comparator):
        if not stop.slots == 1:
            raise ValueError("Too many slots on stop comparator.")
        start = wanderer.indices.count.value if start is None else start
        start = 0 if start is None else start
        try:
            start = wanderer.process_configs(start, strict = True)
        except CannotProcessConfigs:
            start = wanderer[0:start]
    assert isinstance(start, Configs)
    assert isinstance(stop, Comparator)
    return start, stop

class Wanderer(Voyager, Configurable):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    @property
    def locality(self):
        return self.configs.id, tuple(i.value for i in self.indices)

    def _configurable_changed_state_hook(self):
        super()._configurable_changed_state_hook()
        self._nullify_indexers()

    def _initialise(self, *args, **kwargs):
        self.configure(silent = True)
        super()._initialise(*args, **kwargs)
        self.configured = False

    def gofrom(self, start, stop):
        start, stop = get_start_stop(self, (start, stop))
        self.set_configs(**start)
        self.go(stop)

    def _out(self, *args, **kwargs):
        if self._indexers_isnull:
            self.initialise()
        return super()._out(*args, **kwargs)

    def _load(self, arg):
        if arg == 0:
            try:
                super()._load(arg)
            except IndexerLoadFail:
                self.initialise()
        else:
            super()._load(arg)
        if not self._indexers_isnull:
            self.configured = False

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
                return State.get_state(self, arg)
            except RedundantState:
                return ImmutableConfigs(contents = self.configs)

    def __setitem__(self, key, val):
        if isinstance(val, Wanderer):
            val = val[:]
        if isinstance(val, State):
            if val.wanderer.hashID == self.hashID:
                if not val.start.id == self.configs.id:
                    self[...] = val.start
                if not self.indices == val.indices:
                    assert self.outputSubKey == val.data.name
                    self.load(val.data)
                return
            else:
                val = val[:]
        super().__setitem__(key, val)
        self.initialise(silent = True)
        return

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configs.contentHash
