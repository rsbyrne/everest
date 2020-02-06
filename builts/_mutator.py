from types import FunctionType

from . import Built
from ..writer import Writer
from ..weaklist import WeakList

class Mutator(Built):
    def __init__(
            self,
            **kwargs
            ):
        self._mutateDict = dict()
        self._update_mutateDict_fns = WeakList()
        super().__init__(**kwargs)
    def mutate(self):
        self._check_anchored()
        for fn in self._update_mutateDict_fns: fn()
        self.writer.add(self._mutateDict, self.hashID)
