from . import Built
from ..weaklist import WeakList

class Applier(Built):
    def __init__(self, **kwargs):
        self._pre_apply_fns = WeakList()
        self._apply_fns = WeakList()
        self._post_apply_fns = WeakList()
        super().__init__(**kwargs)
        self.__call__ = self.apply
    def apply(self, arg):
        for fn in self._pre_apply_fns: fn()
        for fn in self._apply_fns: fn(arg)
        for fn in self._post_apply_fns: fn()
