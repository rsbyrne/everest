################################################################################

import weakref

from . import _Function

class Base(_Function):
    def __init__(self, *, name: str, **kwargs) -> None:
        self.downstream = weakref.WeakSet()
        super().__init__(name = name, **kwargs)
    def register_downstream(self, registrant):
        self.downstream.add(registrant)
    def refresh(self):
        for down in self.downstream:
            down.purge()

################################################################################
