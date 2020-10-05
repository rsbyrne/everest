from functools import wraps
from collections.abc import Mapping, Sequence
from collections import OrderedDict

from ._producer import Producer
from ._mutable import Mutable
from ._applier import Applier
from . import w_hash

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
class ConfigurableException(BuiltException):
    pass
class ConfigurableMissingMethod(MissingMethod, ConfigurableException):
    pass
class ConfigurableMissingAttribute(MissingAttribute, ConfigurableException):
    pass
class ConfigurableMissingKwarg(MissingKwarg, ConfigurableException):
    pass
class NotConfigured(ConfigurableException):
    pass

class Configs(Pyklet, Mapping, Sequence):
    def __init__(self, *args, new = None, **kwargs):
        if not len(args):
            self._contents = OrderedDict()
            self.defaults = OrderedDict()
        else:
            args = list(args)
            self.defaults = OrderedDict(args.pop(0))
            args = tuple(args)
            if new is None:
                self._contents = self._process_new(new)
            else:
                self._contents = self._align_inputs(*args, **kwargs)
        super().__init__(self.defaults, {'new': self._contents})
    def _process_new(self, new):
        defaults = self.defaults
        if new is None:
            return OrderedDict({**defaults})
        elif isinstance(new, Mapping):
            return cls._align_inputs(defaults, **new)
        elif isinstance(new, Sequence):
            return cls._align_inputs(defaults, *new)
        else:
            raise ValueError
    def _align_inputs(cls, *args, **kwargs):
        defaults = self.defaults
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
    def clear(self):
        self.update({})
    def update(self, inDict):
        self._contents.clear()
        self._contents.update(self._align_inputs(**inDict))
    def update_generic(self, *args, **kwargs):
        self._contents.clear()
        self._contents.update(self._align_inputs(*args, **kwargs))
    def __len__(self):
        return len(self._contents)
    @property
    def hashID(self):
        return w_hash(self)

def _configured(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.configured:
            raise NotConfigured
        return func(self, *args, **kwargs)
    return wrapper
def _reconfigured(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        out = func(self, *args, **kwargs)
        self._configurable_post_reconfigured()
        return out
    return wrapper

class Configurable(Producer, Mutable):

    _defaultConfigsKey = 'configs'

    def __init__(self, _defaultConfigs = None, **kwargs):

        if _defaultConfigs is None:
            raise ConfigurableMissingKwarg
        try:
            _defaultConfigs = OrderedDict(_defaultConfigs)
        except TypeError:
            _defaultConfigs = OrderedDict([k, None for k in _defaultConfigs])
        if isinstance(_defaultConfigs, Ma)
        self.configs = Configs(_defaultConfigs)
        self.configsKey = self._defaultConfigsKey

        super().__init__(_mutableKeys = self.configs.keys(), **kwargs)

    @_reconfigured
    def configure(self, *args, **kwargs):
        self.configs.update_generic(*args, **kwargs)
        self.configs.update(_process_configs(self.configs))
        self._configure()
    def _process_configs(self, configs):
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
    @property
    def configured(self):
        return all([*self._configured()])
    def _configured(self):
        yield True
    def _configurable_post_reconfigured(self):
        pass

    @_configured
    def _outputSubKey(self):
        for o in super()._outputSubKey(): yield o
        yield self.configs.hashID

    @_configured
    def _save(self):
        self.writeouts.add_dict({self.configsKey: self.configs})
        super()._save()
