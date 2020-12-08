from ptolemaic import Case

from ptolemaic.frames.stateful import State
from ptolemaic.utilities import inner_class

from ._iterable import Iterable
from ._configurable import Configurable

from ..exceptions import *
class TraversableException(EverestException):
    pass

class Traversable(Iterable, Configurable):

    def initialise(self):
        self._subInstantiable_change_state_hook()
        super().initialise()

    def _subInstantiable_change_state_hook(self):
        super()._subInstantiable_change_state_hook()
        self.indices.nullify()

    @inner_class(Iterable, Configurable)
    class StateVar:
        def _set_value(self, mutator):
            try:
                if v.sourceInstanceID == self.sourceInstanceID:
                    raise ValueError("Circular state var reference.")
            except AttributeError:
                pass
            super()._set_value(mutator)

    # @classmethod
    # def _frameClasses(cls):
    #     d = super()._frameClasses()
    #     d['StateVar'][0].append(TraversableVar)
    #     d['Case'][0].insert(0, TraversableCase)
    #     return d

    # def reach(self, configs, *args, **kwargs):
    #     self.configs[...] = configs
    #     if args:
    #         super().reach(*args, **kwargs)
    # def run(self, configs, *args, **kwargs):
    #     self.configs[...] = configs
    #     if args:
    #         super().run(*args, **kwargs)
