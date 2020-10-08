import numpy as np

from ..utilities import w_hash
from ._voyager import Voyager
from ._stampable import Stampable, Stamper
from ._configurable import \
    Configurable, _configurable_configure_if_necessary, Configs
from .. import exceptions
from ..comparator import Comparator, Prop

class WandererException(exceptions.EverestException):
    pass

class State(Stamper):
    def __init__(self, wanderer, slicer):
        self.wanderer = wanderer
        start, stop, step = slicer.start, slicer.stop, slicer.step
        start = Configs(wanderer.configs, new = start)
        stop = False if stop is None else self._process_endpoint(stop)
        step = 1 if step is None else step
        self.start, self.stop, self.step = start, stop, step
        hashID = w_hash((self.wanderer, self.start, self.stop, self.step))
        super().__init__(
            self.wanderer,
            slice(self.start, self.stop, self.step),
            hashID = hashID
            )
    def _process_endpoint(self, arg):
        if isinstance(arg, Comparator):
            return arg
        else:
            try:
                return self.wanderer._indexer_process_endpoint(arg)
            except IndexError:
                pass
            raise TypeError
    # def __getitem__(self, key):
    #     self.configs[key]
    def __enter__(self):
        self._oldConfigs = self.wanderer.configs.copy()
        if self.wanderer.initialised:
            self._reloadVals = self.wanderer.outs.data
        else:
            self._reloadVals = None
        self.wanderer.set_configs(**self.start)
        while not self.stop:
            self.wanderer.iterate(self.step)
        return self.wanderer.outs.data
    def __exit__(self, *args):
        self.wanderer.set_configs(**self._oldConfigs)
        if not self._reloadVals is None:
            self.wanderer.load_raw(self._reloadVals)
        del self._oldConfigs, self._reloadVals
    @property
    def out(self):
        with self as out:
            return out

class Wanderer(Voyager, Configurable):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def _configure(self):
        super()._configure()
        self._nullify_indexers()
        self.initialised = False

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
