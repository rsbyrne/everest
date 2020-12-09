from ptolemaic import Case

from ptolemaic.frames.stateful import State
from ptolemaic.utilities import inner_class

from ._iterable import Iterable
from ._configurable import Configurable

from ..exceptions import *
class TraversableException(EverestException):
    pass

class Traversable(Iterable, Configurable):

    def __init__(self,
            *args,
            **kwargs
            ):
        super().__init__(*args, **kwargs)
        self.configs.indices = self.indices

    def _initialise(self):
        super()._initialise()
        self.configs.apply()

    @inner_class(Iterable, Configurable)
    class Configs:
        def __setitem__(self, *args, **kwargs):
            super().__setitem__(*args, **kwargs)
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
