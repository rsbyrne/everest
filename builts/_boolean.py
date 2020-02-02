from types import FunctionType

from . import Built

class Boolean(Built):
    def __init__(
            self,
            _bool_meta_fn = all,
            **kwargs
            ):
        self._pre_bool_fns = []
        self._bool_fns = []
        self._post_bool_fns = []
        self._bool_meta_fn = _bool_meta_fn
        super().__init__(**kwargs)
    def __bool__(self):
        for fn in self._pre_bool_fns: fn()
        truths = [fn() for fn in self._bool_fns]
        truth = self._bool_meta_fn(truths)
        for fn in self._post_bool_fns: fn()
        return truth
