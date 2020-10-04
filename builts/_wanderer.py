import numpy as np
from functools import wraps, partial
from contextlib import contextmanager

from . import Built, Meta, w_hash
from ._applier import Applier
from ._voyager import Voyager
from ..exceptions import EverestException, NotYetImplemented
from ..weaklist import WeakList
from ..pyklet import Pyklet


class NotConfigured(EverestException):
    '''
    Objects inheriting from Wanderer must be configured before use \
    - see the 'configure' method.
    '''

def _configured(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'configs'):
            raise NotConfigured
        return func(self, *args, **kwargs)
    return wrapper


class Configs(dict):
    @property
    def hashID(self):
        return w_hash(self)

class Wanderer(Voyager):

    def __init__(self, **kwargs):

        self.configs = Configs()
        self._wanderer_configure_pre_fns = WeakList()
        self._wanderer_configure_post_fns = WeakList()

        super().__init__(**kwargs)

    @_configured
    def _save(self):
        self.writeouts.add_dict({'configs': self.configs})
        super()._save()

    def _process_configs(self, configs):
        # expects to be overridden:
        return configs

    def _configure(self):
        ms, cs = self.mutables, self.configs
        for k in sorted(set(ms).intersection(set(cs))):
            m, c = ms[k], cs[k]
            if type(c) is float:
                if not c < float('inf'):
                    c = None
            if not c is None:
                if isinstance(c, Applier):
                    c.apply(m)
                elif hasattr(m, 'data'):
                    m.data[...] = c
                else:
                    m[...] = c

    def configure(self, *argConfigs, **kwargConfigs):
        argConfigs = {
            k: v for k, v in dict(zip(self.configsKeys, argConfigs))
                if not v is None
            }
        configs = {**self.configs, **argConfigs, **kwargConfigs}
        for fn in self._wanderer_configure_pre_fns: fn()
        self.count.value = -1
        self.configs.clear()
        self.configs.update(self._process_configs(**configs))
        self.initialised = False
        self._configure()
        for fn in self._wanderer_configure_post_fns: fn()

    @_configured
    def _outputSubKey(self):
        for o in super()._outputSubKey(): yield o
        yield self.configs.hashID

    @_configured
    def initialise(self):
        # Overrides Producer method:
        super().initialise()

    def __getitem__(self, arg):
        if type(arg) is tuple:
            raise NotYetImplemented
        elif type(arg) is int:
            return self.bounce(arg)
        elif type(arg) is dict:
            return self.bounce(Configs(arg))
        elif type(arg) is slice:
            if slice.step is None:
                return self._get_express(arg)
        return self.configs[arg]
    def _get_express(self, arg):
        start, stop = slice.start, slice.stop
        # sel
    def __setitem__(self, arg1, arg2):
        if type(arg1) is tuple:
            raise NotYetImplemented
        elif type(arg1) is slice:
            raise NotYetImplemented
        elif arg1 is Ellipsis:
            if type(arg2) is dict:
                self.configure(**arg2)
            else:
                self.configure(**dict(zip(self.configsKeys, arg2)))
        elif type(arg1) is str:
            self.configure(**{arg1: arg2})
        else:
            raise ValueError("Input type not supported.")

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configs.hashID
