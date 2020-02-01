from . import Built

class Cycler(Built):
    def __init__(self):
        self._pre_cycle_fns = []
        self._cycle_fns = []
        self._post_cycle_fns = []
        super().__init__()
    def cycle(self):
        for fn in self._pre_cycle_fns: fn()
        for fn in self._cycle_fns: fn()
        for fn in self._post_cycle_fns: fn()
    def __call__(self):
        return self.cycle()
