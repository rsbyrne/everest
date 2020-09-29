import numpy as np
from functools import wraps

from . import Built, Meta, make_hash
from ._voyager import Voyager, LoadFail, _initialised
from ..exceptions import EverestException, NotYetImplemented
from .. import wordhash
wHash = lambda x: wordhash.get_random_phrase(make_hash(x))

class NotConfigured(EverestException):
    '''Objects inheriting from Wanderer must be configured before use - see the 'configure' method.'''

def _configured(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.configs is None:
            raise NotConfigured
        return func(self, *args, **kwargs)
    return wrapper

class Wanderer(Voyager):

    def __init__(self, **kwargs):

        # Expects:
        # self._process_configs
        # self._configure

        if not hasattr(self, 'configs'):
            self.configs = None

        super().__init__(**kwargs)

        # Producer attributes:
        self._pre_save_fns.append(self._wanderer_pre_save_fn)
        self._post_save_fns.append(self._wanderer_post_save_fn)
        self._post_reroute_outputs_fns.append(self._wanderer_post_reroute_fn)

    @_configured
    def _wanderer_pre_save_fn(self):
        pass

    def _wanderer_post_save_fn(self):
        self.writeouts.add_dict({'configs': self.configs})

    def _wanderer_post_reroute_fn(self):
        if hasattr(self, 'chron'):
            self.chron.value = float('NaN')

    def _process_configs(self, configs):
        # expects to be overridden:
        return configs

    def _configure(self):
        # expects to be overridden:
        pass

    def configure(self, configs):
        self.configs = self._process_configs(configs)
        self.configsHash = wHash(self.configs)
        self.reroute_outputs(self.configsHash)
        self.initialised = False
        self._configure()

    def __getitem__(self, arg):
        if type(arg) is tuple:
            raise NotYetImplemented
        elif type(arg) is slice:
            raise NotYetImplemented
        else:
            out = self.__class__(**self.inputs)
            out.configure(arg)
            return out
