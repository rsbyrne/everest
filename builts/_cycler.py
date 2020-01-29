from types import FunctionType

from . import Built

class Cycler(Built):
    def __init__(
            self,
            cycleFn : FunctionType,
            **kwargs
            ):
        self._cycle = cycleFn
        super().__init__(**kwargs)
    def _pre_cycle_hook(self):
        pass
    def cycle(self):
        self._pre_cycle_hook()
        self._cycle()
        self._post_cycle_hook()
    def _post_cycle_hook(self):
        pass
