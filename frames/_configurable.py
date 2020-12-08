from collections.abc import Mapping
from collections import OrderedDict

import numpy as np

from ptolemaic.frames.stateful import Stateful, State, DynamicState, MutableState

from ._configurator import Configurator
from ._suboutputable import SubOutputable
from ..utilities import ordered_unpack
from ..exceptions import *

class Configs(State):
    def __init__(self,
            contents
            ):
        self._vars = OrderedDict(
            (k, self._process_config(v))
                for k, v in contents.items()
            )
        super().__init__()
    @staticmethod
    def _process_config(v):
        if isinstance(v, Configurator):
            return v
        else:
            if v is None:
                v = float('nan')
            return v

class MutableConfigs(MutableState, Configs):
    def __init__(self, defaults):
        super().__init__(defaults)
        self.defaults = self.vars.copy()
    def __setitem__(self, arg1, arg2):
        for k, v in ordered_unpack(self.keys(), arg1, arg2).items():
            if not k in self.keys():
                raise KeyError("Key not in configs: ", k)
            v = self[k] if v is None else self._process_config(v)
            super().__setitem__(k, v)
    def reset(self):
        self.update(self.defaults)
    def update(self, arg):
        self[...] = arg
    def copy(self):
        out = MutableConfigs(self.defaults)
        out.update(self.vars)
        return out

    # def store(self):
    #     k, v = self.id, Configs(contents = self.vars)
    #     self.stored[k] = v
    # def load(self, id):
    #     self.update(self.stored[id])
    #
    # def __setitem__(self, key, val):
    #     super().__setitem__(key, val)
    #     self.frame._configurable_changed_state_hook()

class Configurable(Stateful, SubOutputable):

    def __init__(self,
            _stateVars = None,
            _subInstantiators = None,
            **kwargs
            ):
        _stateVars = [] if _stateVars is None else _stateVars
        _subInstantiators = \
            OrderedDict() if _subInstantiators is None else _subInstantiators
        self.configs = self.Configs(self)
        _stateVars.extend(self.configs.stateVars)
        _subInstantiators['configs'] = (self.configs)
        super().__init__(
            _stateVars = _stateVars,
            _subInstantiators = _subInstantiators,
            **kwargs
            )

    def reset(self):
        self.configs.reset()
        super().reset()

    def _subInstantiable_change_state_hook(self):
        super()._subInstantiable_change_state_hook()
        self.configs.apply(self.state)

    class Configs(MutableConfigs):

        def __init__(self, frame):
            self.sourceInstanceHash = frame.instanceHash
            self._stateVarClass = frame.StateVar
            defaults = OrderedDict(**frame.ghosts.configs)
            super().__init__(defaults)
            self.stored = OrderedDict()
            self.stateVars = [self._process_default(k, v) for k, v in self.items()]
        def _process_default(self, k, v):
            if isinstance(v, self._stateVarClass):
                return v
            elif type(v) is tuple:
                return v[0](v[1], name = k)
            else:
                return self._stateVarClass(v, name = k)
        def __repr__(self):
            return f'{super().__repr__()}({self.sourceInstanceHash})'

    # @classmethod
    # def _frameClasses(cls):
    #     d = super()._frameClasses()
    #     d['Configs'] = ([FrameConfigs,], OrderedDict())
    #     return d

    # def __setitem__(self, key, val):
    #     if type(key) is tuple:
    #         raise ValueError
    #     if type(key) is slice:
    #         raise NotYetImplemented
    #     self.configs[key] = val
    #     self._configurable_changed_state_hook()

    # def _save(self):
    #     super()._save()
    #     self.writeouts.add_dict({'configs': self.configs.vars})

    # def _load(self, arg, **kwargs):
    #     if arg is None:
    #         self.configs.apply()
    #     elif type(arg) is str:
    #         try:
    #             self.configs.load(arg)
    #         except KeyError:
    #             # may be problematic
    #             readpath = '/'.join([
    #                 self.outputMasterKey,
    #                 arg,
    #                 'configs',
    #                 ])
    #             self.configs[...] = self.reader[readpath]
    #     else:
    #         super()._load(arg, **kwargs)
