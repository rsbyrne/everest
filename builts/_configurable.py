from functools import wraps
from collections.abc import Mapping, Sequence
from collections import OrderedDict

import numpy as np

from ._producer import Producer
from ._mutable import Mutable
from ._applier import Applier
from ._configurator import Configurator
from ..pyklet import Pyklet
from ..utilities import w_hash

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
from ..exceptions import NotYetImplemented
class ConfigurableException(BuiltException):
    pass
class ConfigurableMissingMethod(MissingMethod, ConfigurableException):
    pass
class ConfigurableMissingAttribute(MissingAttribute, ConfigurableException):
    pass
class ConfigurableMissingKwarg(MissingKwarg, ConfigurableException):
    pass
class ConfigurableAlreadyConfigure(ConfigurableException):
    pass

class Config(Pyklet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Configs(Pyklet, Mapping, Sequence):
    def __init__(self, defaults, *args, new = None, **kwargs):
        if type(defaults) is type(self):
            defaults = defaults._contents.copy()
        elif not type(defaults) is OrderedDict:
            raise TypeError
        self.defaults = defaults
        self._contents = self._align_inputs(*args, **kwargs)
        self._contents.update(self._process_new(new))
        super().__init__(self.defaults, **{'new': self._contents})
    def _hashID(self):
        return w_hash(tuple(self.items()))
    def _process_new(self, new):
        if new is None:
            return dict()
        elif isinstance(new, Mapping):
            return {**new}
        elif isinstance(new, Sequence):
            return dict(zip(self.defaults.keys(), new))
        else:
            raise TypeError
    def _align_inputs(self, *args, **kwargs):
        ks = self.defaults.keys()
        new = {
            **self.defaults,
            **{k: v for k, v in zip(ks, args) if not v is None},
            **kwargs,
            }
        if not set(new.keys()) == set(ks):
            raise ValueError(
                "Keys did not match up:",
                (new.keys(), ks),
                )
        return OrderedDict([(k, new[k]) for k in ks])
    @staticmethod
    def _check_val(val):
        if not any([
                isinstance(val, (Config, Configurator)),
                issubclass(type(val), (np.int, np.float)),
                isinstance(type(val), np.ndarray),
                val is Ellipsis,
                ]):
            raise TypeError(val, type(val))
    def __getitem__(self, arg):
        if type(arg) is str:
            return self._contents[arg]
        else:
            return list(self._contents.values())[arg]
    def __setitem__(self, arg1, arg2):
        self._check_val(arg2)
        if type(arg1) is str:
            if not arg1 in self.keys():
                raise KeyError
            self._contents[arg1] = arg2
        elif issubclass(type(arg1), np.int):
            self._contents[self.keys()[arg1]] = arg2
        elif type(arg1) is slice:
            rekeys = self.keys()[arg1]
            for k in rekeys:
                self._contents[k] = arg2
        else:
            raise ValueError
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
    def keys(self, *args, **kwargs):
        return list(self._contents.keys(*args, **kwargs))
    def items(self, *args, **kwargs):
        return self._contents.items(*args, **kwargs)
    def clear(self):
        self._contents.update(self.defaults)
    def update(self, inDict):
        for k, v in inDict.items():
            self[k] = v
    def update_generic(self, *args, **kwargs):
        self._contents.clear()
        self._contents.update(self._align_inputs(*args, **kwargs))
    def copy(self):
        return self.__class__(self.defaults, new = self._contents.copy())
    def __len__(self):
        return len(self._contents)

class Configurable(Producer, Mutable):

    _defaultConfigsKey = 'configs'

    def __init__(self, _defaultConfigs = None, **kwargs):

        self.configured = False

        if _defaultConfigs is None:
            raise ConfigurableMissingKwarg
        try:
            _defaultConfigs = OrderedDict(_defaultConfigs)
        except TypeError:
            _defaultConfigs = OrderedDict([(k, None) for k in _defaultConfigs])
        self.configs = Configs(_defaultConfigs)
        self.configsKey = self._defaultConfigsKey

        super().__init__(_mutableKeys = self.configs.keys(), **kwargs)

    def set_configs(self, *args, **kwargs):
        prevHash = self.configs.hashID
        self._set_configs(*args, **kwargs)
        newHash = self.configs.hashID
        self.configured = newHash == prevHash
    def _set_configs(self, *args, **kwargs):
        self.configs.update_generic(*args, **kwargs)
        self.configs.update(self._process_configs(self.configs))
        # self.configure()
    def _process_configs(self, configs):
        return configs
    def configure(self, silent = False):
        if self.configured:
            if silent:
                pass
            else:
                raise ConfigurableAlreadyConfigure
        else:
            self._configure()
    def _configure(self):
        ms, cs = self.mutables, self.configs
        ks = [k for k in self.configs.keys() if k in self.mutables.keys()]
        for k in ks:
            m, c = ms[k], cs[k]
            if not c is Ellipsis:
                if isinstance(c, (Configurator, Config)):
                    c.apply(m)
                elif hasattr(m, 'data'):
                    m.data[...] = c
                else:
                    m[...] = c
        self.configured = True

    def _outputSubKey(self):
        for o in super()._outputSubKey(): yield o
        yield self.configs.hashID

    def _save(self):
        self.writeouts.add_dict({self.configsKey: {**self.configs}})
        super()._save()

    def __setitem__(self, arg1, arg2):
        assert len(self.configs)
        if len(self.configs) == 1:
            self._configurable_set_single(arg1, arg2)
        else:
            self._configurable_set_multi(arg1, arg2)
    def _configurable_set_single(self, arg1, arg2):
        raise NotYetImplemented
    def _configurable_set_multi(self, arg1, arg2):
        if type(arg1) is str:
            self.set_configs(**{arg1: arg2})
        elif arg1 is Ellipsis:
            if type(arg2) is tuple:
                self.set_configs(*arg2)
            else:
                self.set_configs(*[arg2 for _ in range(len(self.configs))])
        else:
            raise TypeError
