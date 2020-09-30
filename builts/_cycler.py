from ..mpi import message
from . import Built
from ..weaklist import WeakList

class Cycler(Built):
    def __init__(self, **kwargs):
        self._pre_cycle_fns = WeakList()
        self._cycle_fns = WeakList()
        self._post_cycle_fns = WeakList()
        super().__init__(**kwargs)
    def __call__(self):
        self.cycle()
    def cycle(self):
        # message("Cycling...", self.__class__, self.hashID)
        for fn in self._pre_cycle_fns: fn()
        outs = []
        for fn in self._cycle_fns: outs.append(fn())
        for fn in self._post_cycle_fns: fn()
        return self._flatten_products(outs)
        # message("Cycled", self.__class__, self.hashID)
