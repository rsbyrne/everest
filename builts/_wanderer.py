import numpy as np
from collections import OrderedDict
from contextlib import contextmanager

from ..utilities import w_hash
from ._producer import NullValueDetected, OutsNull
from ._voyager import Voyager
from ._stampable import Stampable, Stamper
from ._configurable import Configurable, Configs, Config
from ._indexer import IndexerLoadRedundant
from .. import exceptions
from ..comparator import Comparator, Prop
from ..pyklet import Pyklet

class WandererException(exceptions.EverestException):
    pass

class State(Stamper):
    def __init__(self, wanderer, slicer, _data = OrderedDict()):
        self.wanderer = wanderer
        if type(slicer) is tuple:
            slicer = slice(*slicer)
        start, stop, step = slicer.start, slicer.stop, slicer.step
        start = Configs(wanderer.configs, new = start)
        stop = False if stop is None else self._process_endpoint(stop)
        if not step is None: raise exceptions.NotYetImplemented
        self.start, self.stop, self.step = start, stop, step
        self._data = OrderedDict()
        self._data.name = start.hashID
        self._hashObjects = [self.wanderer, (self.start, self.stop, self.step)]
        super().__init__(*[*self._hashObjects, self._data])
    def _process_endpoint(self, arg):
        if isinstance(arg, Comparator):
            self._indexerComparator = True
            return arg
        else:
            try:
                self._indexerComparator = False
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
    def data(self):
        if not len(self._data):
            with self:
                pass
        return self._data
    def __getitem__(self, arg):
        return Statelet(self, arg)

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
    def var(self):
        return self.state.wanderer.mutables[self.channel]
    @contextmanager
    def temp_data(self):
        oldData = self.var.data.copy()
        try:
            self.var.data[...] = self.data
            yield None
        finally:
            self.var.data[...] = oldData
    def apply(self, toVar):
        with self.temp_data():
            toVar.imitate(self.var)

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
        if not type(arg) is slice:
            arg = slice(arg)
        return State(self, arg)

    def __setitem__(self, *args, **kwargs):
        super().__setitem__(*args, **kwargs)
        self.initialise(silent = True)

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configs.hashID
