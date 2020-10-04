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

def _configured(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not len(self.configs):
            raise NotConfigured
        return func(self, *args, **kwargs)
    return wrapper

class State(Pyklet, Mapping):
    def __init__(self, wanderer, *args, final = None, **kwargs):
        if final is None:
            try:
                final = args.pop(-1)
            except IndexError:
                raise ValueError("No 'final' argument was provided.")
        self.configs = Configs(wanderer.configs, *args, **kwargs)
        self.wanderer = wanderer
        self.final = self._process_endpoint(final)
        self.hashID = w_hash((self.wanderer, self.configs, self.final))
        super(self.wanderer, **configs)
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
        self.wanderer.go(self.final)
        return None
    def __exit__(self, *args):
        self.wanderer.configure(**self._oldConfigs)
        if not self._reloadVals is None:
            self.wanderer.load_raw(self._reloadVals)
        del self._oldConfigs, self._reloadVals

class Configs(Mapping, Sequence):
    def __init__(self, defaults, *args, **kwargs):
        self._contents = self._align_inputs(defaults, *args, **kwargs)
    @staticmethod
    def _align_inputs(defaults, *args, **kwargs):
        ks = defaults.keys()
        new = {
            **defaults,
            **{k: v for k, v in zip(ks, args) if not v is None},
            **kwargs,
            }
        if not new.keys() == ks:
            raise ValueError(
                "Keys did not match up:",
                (new.keys(), ks),
                )
        new = OrderedDict([(k, new[k]) for k in ks])
        return new
    def __getitem__(self, arg):
        if type(arg) is str:
            return self._contents[arg]
        else:
            return list(self._contents.values())[arg]
    def __setitem__(self, arg1, arg2):
        if type(arg1) is str:
            self._contents[arg1] = arg2
        elif issubclass(type(arg1), np.int):
            self._contents[self.keys()[arg1]] = arg2
        elif type(arg1) is slice:
            rekeys = self.keys()[arg1]
            for k in rekeys:
                self._contents[k] = arg2
        else:
            raise ValueError
    def keys(self):
        return list(self._contents.keys())
    def __len__(self):
        return len(self._contents)
    @property
    def hashID(self):
        return w_hash(self)

class Wanderer(Voyager):

    def __init__(self, **kwargs):

        self.configs = Configs()
        self._wanderer_configure_pre_fns = WeakList()
        self._wanderer_configure_post_fns = WeakList()

        super().__init__(**kwargs)

    def configure(self, *args, **kwargs):
        configs = Configs(self.configs, *args, **kwargs)
        for fn in self._wanderer_configure_pre_fns: fn()
        self.count.value = -1
        self.configs.clear()
        self.configs.update(self._process_configs(**configs))
        self.initialised = False
        self._configure()
        for fn in self._wanderer_configure_post_fns: fn()

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

    def _process_configs(self, configs):
        # expects to be overridden:
        return configs

    @_configured
    def initialise(self):
        # Overrides Producer method:
        super().initialise()

    @_configured
    def _outputSubKey(self):
        for o in super()._outputSubKey(): yield o
        yield self.configs.hashID

    @_configured
    def _save(self):
        self.writeouts.add_dict({'configs': self.configs})
        super()._save()

    @_configured
    def __getitem__(self, arg):
        assert len(self.configsKeys)
        if len(self.configsKeys) == 1:
            return self._wanderer_get_single(arg)
        else:
            return self._wanderer_get_multi(arg)
    def _wanderer_get_single(arg):
        raise exceptions.NotYetImplemented
    def _wanderer_get_multi(arg):
        raise exceptions.NotYetImplemented

    @_configured
    def __setitem__(self, arg1, arg2):
        assert len(self.configsKeys)
        if len(self.configsKeys) == 1:
            return self._wanderer_set_single(arg1, arg2)
        else:
            return self._wanderer_set_multi(arg1, arg2)
    def _wanderer_set_single(arg):
        raise exceptions.NotYetImplemented
    def _wanderer_set_multi(arg):
        raise exceptions.NotYetImplemented
    #
    # def __getitem__(self, arg):
    #     if type(arg) is tuple:
    #         raise exceptions.NotYetImplemented
    #     elif type(arg) is int:
    #         raise exceptions.NotYetImplemented
    #     elif type(arg) is dict:
    #         raise exceptions.NotYetImplemented
    #     elif type(arg) is slice:
    #         if slice.step is None:
    #             return State(
    #                 self,
    #                 final = slice.stop,
    #                 **Configs(slice.start)
    #                 )
    #         else:
    #             raise exceptions.NotYetImplemented
    #     else:
    #         raise TypeError
    # def __setitem__(self, arg1, arg2):
    #     if type(arg1) is tuple:
    #         if not type(arg2)
    #         self.configure(dict(zip()))
    #         raise exceptions.NotYetImplemented
    #     elif type(arg1) is slice:
    #         raise exceptions.NotYetImplemented
    #     elif arg1 is Ellipsis:
    #         if len(self.configsKeys) == 1:
    #             raise
    #         if isinstance(arg2, Mapping):
    #             self.configure(**arg2)
    #         elif isinstance(arg2, Sequence):
    #             self.configure(*arg2)
    #         else:
    #             self.configure(arg2)
    #     elif type(arg1) is str:
    #         self.configure(**{arg1: arg2})
    #     else:
    #         raise ValueError("Input type not supported.")

    @property
    def _promptableKey(self):
        # Overrides Promptable property:
        return self.configs.hashID
