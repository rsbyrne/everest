from functools import wraps
from collections.abc import Mapping, Sequence
from collections import OrderedDict
import warnings

import numpy as np

from . import Proxy
from ._stateful import Stateful, Statelet, State
from ._applier import Applier
from ._configurator import Configurator
from ..pyklet import Pyklet
from ..utilities import w_hash, get_hash, is_numeric

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
class ConfigurableAlreadyConfigured(ConfigurableException):
    pass
class CannotProcessConfigs(ConfigurableException):
    pass
class ConfigException(EverestException):
    pass
class ConfigMissingMethod(MissingMethod, ConfigException):
    pass
class ConfigCannotConvert(ConfigException):
    pass
class ConfigsException(EverestException):
    pass
class ConfigsMissingAttribute(EverestException):
    pass

class Config(Pyklet):
    def __init__(self, *args, content = None, **kwargs):
        self.content = content
        super().__init__(*args, content = content, **kwargs)
    def _hashID(self):
        return get_hash(self.content, make = True)
    def apply(self, toVar):
        if not isinstance(toVar, Statelet):
            raise TypeError(type(toVar))
        self._apply(toVar)
    def _apply(self, toVar):
        toVar.mutate(self.content)
    @classmethod
    def convert(cls, arg, default = None, strict = False):
        if default is Ellipsis and not arg is Ellipsis:
            warnings.warn('Cannot reset Ellipsis default config: ignoring.')
            return Ellipsis
        else:
            if isinstance(arg, Proxy):
                arg = arg.realised
            if any([
                    isinstance(arg, (Config, Configurator)),
                    arg is Ellipsis,
                    ]):
                return arg
            elif not strict and any([
                    is_numeric(arg),
                    isinstance(type(arg), np.ndarray),
                    ]):
                return arg
            else:
                raise ConfigCannotConvert(repr(arg)[:100], type(arg))
    # @property
    # def var(self):
    #     return self._var()
    # def _var(self):
    #     raise ConfigMissingMethod

class Configs(Pyklet, Mapping, Sequence):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def _hashID(self):
        return w_hash(tuple(self.contents.items()))
    @property
    def contents(self):
        return self._contentsDict
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
    def apply(self, state):
        if not isinstance(state, State):
            raise TypeError
        if not [*state.keys()] == [*self.keys()]:
            raise KeyError(state.keys(), self.keys())
        self._apply(state)
    def _apply(self, state):
        if not isinstance(state, State):
            raise TypeError("Configs can only be applied to State.")
        for c, m in zip(self.values(), state):
            if not c is Ellipsis:
                if isinstance(c, (Configurator, Config)):
                    c.apply(m)
                else:
                    m.mutate(c)
    @property
    def id(self):
        return self.contentHash
class MutableConfigs(Configs):
    def __init__(self, defaults, *args, contents = None, **kwargs):
        if type(defaults) is type(self):
            defaults = defaults.contents.copy()
        elif not type(defaults) is OrderedDict:
            raise TypeError
        self.defaults = defaults
        self._contentsDict = self._align_inputs(*args, **kwargs)
        self._contentsDict.update(self._process_new(contents))
        for k, v in self._contentsDict.items():
            self._contentsDict[k] = Config.convert(v, self.defaults[k])
        super().__init__(
            defaults = self.defaults,
            contents = self._contentsDict,
            **kwargs,
            )
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
    def __setitem__(self, arg1, arg2):
        arg2 = Config.convert(arg2, self.defaults[arg1])
        if type(arg1) is str:
            if not arg1 in self.keys():
                raise KeyError
            self.contents[arg1] = arg2
        elif issubclass(type(arg1), np.integer):
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
        self._contentsDict = contents.copy()
        super().__init__(*args, contents = contents, **kwargs)

class Configurable(Stateful):

    _defaultConfigsKey = 'configs'

    def __init__(self, _defaultConfigs = None, **kwargs):

        if _defaultConfigs is None:
            _defaultConfigs = OrderedDict(
                (k, self.ghosts[k]) for k in self._sortedGhostKeys['configs']
                )
        for k, v in _defaultConfigs.items():
            if v is None:
                _defaultConfigs[k] = float('NaN')

        self.configured = False
        self._storedConfigs = OrderedDict()

        if _defaultConfigs is None:
            raise ConfigurableMissingKwarg
        try:
            _defaultConfigs = OrderedDict(_defaultConfigs)
        except TypeError:
            _defaultConfigs = OrderedDict([(k, None) for k in _defaultConfigs])
        self.configs = MutableConfigs(_defaultConfigs)
        self.configsKey = self._defaultConfigsKey
        self.configsKeys = tuple(self.configs.keys())

        super().__init__(**kwargs)

    def _state_keys(self):
        for k in super()._state_keys(): yield k
        for k in self.configs.keys(): yield k

    def set_configs(self, *args, new = None, **kwargs):
        prevHash = self.configs.contentHash
        self._set_configs(*args, new = new, **kwargs)
        newHash = self.configs.contentHash
        self.configured = newHash == prevHash and self.configured
        if newHash != prevHash:
            self._configurable_changed_state_hook()
    def _set_configs(self, *args, new = None, **kwargs):
        if new is None:
            new = self.merge_configs(*args, **kwargs)
        else:
            if len(args) or len(kwargs):
                raise ValueError
            new = self.process_configs(new)
        self.configs.update(new)
    def merge_configs(self, *args, **kwargs):
        merged = self.configs.copy()
        merged.update_generic(*args, **kwargs)
        return merged
    def process_configs(self, arg, strict = False):
        try:
            return self.merge_configs(Config.convert(arg, strict = strict))
        except ConfigCannotConvert:
            if isinstance(arg, Sequence):
                return self.merge_configs(*arg)
            elif isinstance(arg, Mapping):
                return self.merge_configs(**arg)
            else:
                raise CannotProcessConfigs
    def configure(self, silent = False):
        if self.configured:
            if silent:
                pass
            else:
                raise ConfigurableAlreadyConfigured
        else:
            self._configure()
    def _configure(self):
        self.configs.apply(self.state)
        self.configured = True
        self._configurable_changed_state_hook()
    def _configurable_changed_state_hook(self):
        pass
    @property
    def storedConfigs(self):
        return self._storedConfigs
    def store_config(self):
        k, v = self.configs.id, ImmutableConfigs(contents = self.configs)
        self.storedConfigs[k] = v

    def _outputSubKey(self):
        for o in super()._outputSubKey(): yield o
        yield self.configs.contentHash

    def _save(self):
        self.writeouts.add_dict({self.configsKey: self.configs.contents})
        super()._save()

    def _load(self, arg):
        if arg is None:
            self.configure(silent = True)
        elif type(arg) is str:
            try:
                loadCon = self.storedConfigs[arg]
            except KeyError:
                readpath = '/'.join([
                    self.outputMasterKey,
                    arg,
                    self.configsKey
                    ])
                loadCon = self.reader[readpath]
            self.set_configs(**loadCon)
        else:
            super()._load(arg)

    def __setitem__(self, arg1, arg2):
        assert len(self.configs)
        if len(self.configs) == 1:
            self._configurable_set_single(arg1, arg2)
        else:
            self._configurable_set_multi(arg1, arg2)
    def _configurable_set_single(self, arg1, arg2):
        raise NotYetImplemented
    def _configurable_set_multi(self, arg1, arg2):
        if arg1 is Ellipsis:
            seqChoice = range(len(self.configs))
            mapChoice = self.configs.keys()
        elif type(arg1) is str:
            seqChoice = [list(self.configs.keys()).index(arg1),]
            mapChoice = [arg1,]
        elif type(arg1) is int:
            seqChoice = [arg1,]
            mapChoice = [list(self.configs.keys())[arg1],]
        elif type(arg1) is tuple:
            if len(set([type(o) for o in arg1])) > 1:
                raise ValueError
            if type(arg1[0]) is str:
                seqFn = lambda arg: list(self.configs.keys()).index(arg)
                seqChoice = [seqFn(arg) for arg in arg1]
                mapChoice = arg1
            elif type(arg1[0] is int):
                mapFn = lambda arg: list(self.configs.keys())[arg]
                seqChoice = arg1
                mapChoice = [mapFn(arg) for arg in arg1]
            else:
                raise TypeError
        if isinstance(arg2, Sequence):
            arg2 = [arg2[i] for i in seqChoice]
            self.set_configs(*arg2)
        elif isinstance(arg2, Mapping):
            arg2 = OrderedDict((k, arg2[k]) for k in mapChoice)
            self.set_configs(**arg2)
        else:
            arg2 = [arg2 for i in seqChoice]
            self.set_configs(*arg2)
