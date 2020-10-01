import numpy as np
from functools import wraps

from . import Built, Meta, make_hash
from ._voyager import Voyager, LoadFail, _initialised
from ..exceptions import EverestException, NotYetImplemented
from .. import wordhash
wHash = lambda x: wordhash.get_random_phrase(make_hash(x))

class NotConfigured(EverestException):
    '''
    Objects inheriting from Wanderer must be configured before use \
    - see the 'configure' method.
    '''

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
        self._outputSubKeys.append(self._wanderer_outputSubKey_fn)

        # Observable attributes:

    @_configured
    def _wanderer_pre_save_fn(self):
        pass

    def _wanderer_post_save_fn(self):
        if not self._observation_mode_active:
            self.writeouts.add_dict({'configs': self.configs})

    def _process_configs(self, configs):
        # expects to be overridden:
        return configs

    def _configure(self):
        # expects to be overridden:
        pass

    @_configured
    def _wanderer_outputSubKey_fn(self):
        return self.configsHash

    def configure(self, configs):
        if hasattr(self, 'chron'):
            self.chron.value = float('NaN')
        self.count.value = -1
        self.configs = self._process_configs(configs)
        self.configsHash = wHash(self.configs)
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
    def __setitem__(self, arg1, arg2):
        assert len(self.configsKeys), "The configs keys dict is empty."
        if arg1 is Ellipsis:
            arg1 = self.configsKeys
        if not type(arg1) is tuple:
            arg1 = arg1,
        if not type(arg2) is tuple:
            arg2 = arg2,
        if len(arg2) > len(arg1):
            raise ValueError(
                "Too many configurations provided:\
                there should be only " + str(len(arg1)) + '.'
                )
        elif len(arg1) > len(arg2):
            if len(arg2) > 1:
                raise ValueError(
                    "Too many configurations provided:\
                    there should be either 1 or " + str(len(arg1)) + '.'
                    )
            arg2 = tuple([arg2[0] for _ in arg1])
        self.configure(dict(zip(arg1, arg2)))

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configsHash
