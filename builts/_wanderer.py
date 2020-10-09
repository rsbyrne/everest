import numpy as np
from collections import OrderedDict

from ..utilities import w_hash
from ._producer import NullValueDetected, OutsNull
from ._voyager import Voyager, _voyager_uninitialise_if_necessary
from ._stampable import Stampable, Stamper
from ._configurable import \
    Configurable, _configurable_configure_if_necessary, Configs
from .. import exceptions
from ..comparator import Comparator, Prop

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
        self._data = OrderedDict([
            (k, OutsNull) for k in self.wanderer.configs.keys()
            ])
        self._hashObjects = [self.wanderer, (self.start, self.stop, self.step)]
        super().__init__(*[*self._hashObjects, self._data])
    def _process_endpoint(self, arg):
        if isinstance(arg, Comparator):
            return arg
        else:
            try:
                return self.wanderer._indexer_process_endpoint(arg)
            except IndexError:
                pass
            raise TypeError
    def __enter__(self):
        self._oldConfigs = self.wanderer.configs.copy()
        if self.wanderer.initialised:
            self._reloadVals = self.wanderer.outs.data.copy()
        else:
            self._reloadVals = None
        self.wanderer.set_configs(**self.start)
        self.wanderer.configure()
        if any([v is OutsNull for v in self._data.values()]):
            self.wanderer.initialise()
            while not self.stop:
                self.wanderer.iterate()
            self._data.update(self.wanderer.outs.data)
        else:
            self.wanderer.load(self._data)
        return self
    def __exit__(self, *args):
        self.wanderer.set_configs(**self._oldConfigs)
        self.wanderer.configure()
        if not self._reloadVals is None:
            self.wanderer.initialise()
            if self.wanderer.indices.count > 0:
                self.wanderer.load(self._reloadVals)
        del self._oldConfigs, self._reloadVals
    @property
    def data(self):
        if not len(self._data) is None:
            with self:
                pass
        return self._data

    # @property
    # def out(self):
    #     with self as out:
    #         return out

class Wanderer(Voyager, Configurable):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    @_voyager_uninitialise_if_necessary
    def _configure(self):
        super()._configure()

    @_configurable_configure_if_necessary
    def _initialise(self, *args, **kwargs):
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

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configs.hashID
