from functools import wraps
from collections.abc import Mapping, Sequence
from collections import OrderedDict

import numpy as np

from ._producer import Producer
from ._mutable import Mutable, Mutant, Mutables
from ._applier import Applier
from ._configurator import Configurator
from ..pyklet import Pyklet
from ..utilities import w_hash

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
from ..exceptions import EverestException, NotYetImplemented
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
class ConfigException(EverestException):
    pass
class ConfigMissingMethod(MissingMethod, ConfigException):
    pass
class ConfigsException(EverestException):
    pass
class ConfigsMissingAttribute(EverestException):
    pass

class Config(Pyklet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def apply(self, toVar):
        if not isinstance(toVar, Mutant):
            raise TypeError(toVar, type(toVar))
        self._apply(toVar)
    def _apply(self, toVar):
        toVar.imitate(self)
    # @property
    # def var(self):
    #     return self._var()
    # def _var(self):
    #     raise ConfigMissingMethod

class Configs(Pyklet, Mapping, Sequence):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def _hashID(self):
        return w_hash(tuple(self.items()))
    @property
    def contents(self):
        raise ConfigsMissingAttribute
    def __getitem__(self, arg):
        if type(arg) is str:
            return self.contents[arg]
        else:
            return list(self.contents.values())[arg]
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]
    def keys(self, *args, **kwargs):
        return list(self.contents.keys(*args, **kwargs))
    def values(self, *args, **kwargs):
        return list(self.contents.values(*args, **kwargs))
    def items(self, *args, **kwargs):
        return self.contents.items(*args, **kwargs)
    def __len__(self):
        return len(self.contents)
    def apply(self, mutables):
        if not isinstance(mutables, Mutables):
            raise TypeError
        if not [*mutables.keys()] == [*self.keys()]:
            raise KeyError(mutables.keys(), self.keys())
        self._apply(mutables)
    def _apply(self, mutables):
        for c, m in zip(self.values(), mutables.values()):
            if not c is Ellipsis:
                if isinstance(c, (Configurator, Config)):
                    c.apply(m)
                elif hasattr(m, 'data'):
                    m.data[...] = c
                else:
                    m[...] = c
class MutableConfigs(Configs):
    def __init__(self, defaults, *args, contents = None, **kwargs):
        if type(defaults) is type(self):
            defaults = defaults.contents.copy()
        elif not type(defaults) is OrderedDict:
            raise TypeError
        self.defaults = defaults
        self._contentsDict = self._align_inputs(*args, **kwargs)
        self._contentsDict.update(self._process_new(contents))
        _ = [self._check_val_type(v) for v in self.values()]
        super().__init__(
            defaults = self.defaults,
            contents = self._contentsDict,
            **kwargs,
            )
    @property
    def contents(self):
        return self._contentsDict
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
    def _check_val_type(val):
        if not any([
                isinstance(val, (Config, Configurator)),
                issubclass(type(val), (np.int, np.float)),
                isinstance(type(val), np.ndarray),
                val is Ellipsis,
                ]):
            raise TypeError(val, type(val))
    @classmethod
    def _process_val(cls, val):
        cls._check_val_type(val)
        return val
    def __setitem__(self, arg1, arg2):
        arg2 = self._process_val(arg2)
        if type(arg1) is str:
            if not arg1 in self.keys():
                raise KeyError
            self.contents[arg1] = arg2
        elif issubclass(type(arg1), np.int):
            self.contents[self.keys()[arg1]] = arg2
        elif type(arg1) is slice:
            rekeys = self.keys()[arg1]
            for k in rekeys:
                self.contents[k] = arg2
        else:
            raise ValueError
    def clear(self):
        self.contents.update(self.defaults)
    def update(self, inDict):
        for k, v in inDict.items():
            self[k] = v
    def update_generic(self, *args, **kwargs):
        self.contents.clear()
        self.contents.update(self._align_inputs(*args, **kwargs))
    def copy(self):
        return type(self)(
            defaults = self.defaults,
            contents = self.contents.copy()
            )
class ImmutableConfigs(Configs):
    def __init__(self, *args, contents = OrderedDict(), **kwargs):
        self._contentsDict = contents
        super().__init__(*args, contents = contents, **kwargs)
    @property
    def contents(self):
        return self._contentsDict

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
        self.configs = MutableConfigs(_defaultConfigs)
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
        self.configs.apply(self.mutables)
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
