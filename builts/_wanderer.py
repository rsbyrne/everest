import numpy as np
from functools import wraps, partial
from contextlib import contextmanager
from collections import OrderedDict
from collections.abc import Mapping, Sequence

from . import Built, Meta, w_hash
from ._applier import Applier
from ._voyager import Voyager
from ._counter import Counter
from ._chroner import Chroner
from .._configurable import Configurable, _configured, _reconfigured
from .. import exceptions
from ..weaklist import WeakList
from ..pyklet import Pyklet
from ..comparator import Comparator, Prop

class WandererException(exceptions.EverestException):
    pass
class WandererStateException(WandererException):
    pass
class NotConfigured(WandererException):
    '''
    Objects inheriting from Wanderer must be configured before use \
    - see the 'configure' method.
    '''

class State(Pyklet, Mapping):
    def __init__(self, wanderer, slicer):
        self.wanderer = wanderer
        start, stop, step = slicer.start, slicer.stop, slicer.step
        start = Configs(wanderer.configs, new = start)
        stop = False if stop is None else self._process_endpoint(stop)
        step = 1 if step is None else step
        self.start, self.stop, self.step = start, stop, step
        super(self.wanderer, slice(self.start, self.stop, self.step))
        self.hashID = w_hash((self.wanderer, self.start, self.stop, self.step))
    def _process_endpoint(self, arg):
        if isinstance(arg, Comparator):
            return arg
        elif issubclass(type(arg), np.number):
            return self.wanderer._process_endpoint(arg)
        else:
            raise exceptions.NotYetImplemented
    def __getitem__(self, key):
        self.configs[key]
    def __enter__(self):
        self._oldConfigs = self.wanderer.configs.copy()
        if self.wanderer.initialised:
            self._reloadVals = self.wanderer.out
        else:
            self._reloadVals = None
        self.wanderer.configure(**self.configs)
        while not self.stop:
            self.wanderer.iterate(self.step)
        return self.wanderer.out
    def __exit__(self, *args):
        self.wanderer.configure(**self._oldConfigs)
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

    def _configurable_post_reconfigured(self):
        super()._configurable_post_reconfigured()
        self._nullify_count()

    @_configured
    def initialise(self):
        super().initialise()

    @_configured
    def __getitem__(self, arg):
        assert len(self.configs)
        if len(self.configs) == 1:
            return self._wanderer_get_single(arg)
        else:
            return self._wanderer_get_multi(arg)
    def _wanderer_get_single(arg):
        raise exceptions.NotYetImplemented
    def _wanderer_get_multi(arg):
        if not type(arg) is slice:
            arg = slice(arg)
        return State(self, arg)

    @_configured
    def __setitem__(self, arg1, arg2):
        assert len(self.configs)
        if len(self.configs) == 1:
            return self._wanderer_set_single(arg1, arg2)
        else:
            return self._wanderer_set_multi(arg1, arg2)
    def _wanderer_set_single(arg):
        raise exceptions.NotYetImplemented
    def _wanderer_set_multi(arg):
        raise exceptions.NotYetImplemented

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configs.hashID
