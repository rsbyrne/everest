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
        wanderer, (start, stop) = cls._state_process(wanderer, slicer)
        obj = cls(wanderer, (start, stop))
        try:
            obj = cls._premade[obj.contentHash]
        except KeyError:
            cls._premade[obj.contentHash] = obj
        return obj
    @classmethod
    def _state_process(cls, wanderer, slicer):
        localWanderer = wanderer.copy()
        localWanderer.set_configs(**wanderer.configs)
        if wanderer._indexers_ispos:
            localWanderer.load(wanderer.outs.data)
        if type(slicer) is tuple:
            slicer = slice(*slicer)
        start, stop, step = slicer.start, slicer.stop, slicer.step
        if not step is None:
            raise ValueError("Cannot specify step for state.")
        stop, _indexerEndpoint = cls._process_endpoint(
            stop,
            localWanderer
            )
        if _indexerEndpoint:
            if not start is None:
                warnings.warn("Specified start point is redundant; ignoring.")
            start, _indexerStartpoint = localWanderer.configs, 0
        else:
            start, _indexerStartpoint = cls._process_startpoint(
                start,
                localWanderer
                )
        return [
            localWanderer,
            (start, stop)
            ]
    @classmethod
    def _process_startpoint(cls, arg, wanderer):
        if isinstance(arg, Comparator):
            raise everest.NotYetImplemented
        try:
            arg = wanderer.process_configs(arg, strict = True)
            _indexerStartpoint = None
            return arg, _indexerStartpoint
        except CannotProcessConfigs:
            arg = swanderer.indices.count.value if arg is None else arg
            arg = 0 if arg is None else arg
            if is_numeric(arg):
                _indexerStartpoint = arg
                if arg == 0:
                    return ImmutableConfigs(contents = wanderer.configs)
                else:
                    return wanderer[0 : arg], _indexerStartpoint
        raise TypeError(type(arg))
    @classmethod
    def _process_endpoint(cls, arg, wanderer):
        if isinstance(arg, Comparator):
            _indexerEndpoint = None
            return arg, _indexerEndpoint
        else:
            try:
                if arg is None:
                    if not wanderer._indexers_ispos:
                        raise RedundantState
                    arg = wanderer.indices.count
                _indexerEndpoint = arg
                endComp = wanderer._indexer_process_endpoint(arg, close = False)
                return endComp, _indexerEndpoint
            except IndexError:
                raise TypeError
    def __init__(self, wanderer, sliceTup):
        self.wanderer, (self.start, self.stop) = wanderer, sliceTup
        self._stateArgs = (self.wanderer, (self.start, self.stop))
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
        self.wanderer.initialise(silent = True)
        while not self.stop(self.wanderer):
            self.wanderer.iterate()
        self._data = self.wanderer.outs.data.copy()
        self._data.name = self.wanderer.outputSubKey
        self._indices = namedtuple('IndexerHost', self.wanderer.indexerKeys)(
            *[i.value for i in self.wanderer.indexers]
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
        return self.wanderer.mutables

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
        assert not self.state.wanderer is toVar.host
        super()._apply(toVar)

    # @property
    # def out(self):
    #     with self as out:
    #         return out

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
