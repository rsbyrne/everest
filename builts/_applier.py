from . import Built

class Applier(Built):
    def __init__(self, **kwargs):
        self._apply_fns = []
        super().__init__(**kwargs)
    def __call__(self, arg):
        for fn in self._apply_fns: fn(arg)
