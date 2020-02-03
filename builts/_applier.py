from ._callable import Callable

class Applier(Callable):
    def __init__(self, **kwargs):
        self._pre_apply_fns = []
        self._apply_fns = []
        self._post_apply_fns = []
        super().__init__(**kwargs)
        self._call_fns.append(self.apply)
    def apply(self, arg):
        for fn in self._pre_apply_fns: fn()
        for fn in self._apply_fns: fn(arg)
        for fn in self._post_apply_fns: fn()
