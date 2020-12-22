from everest.funcy.base import Function

from .exceptions import *

class Datalike(Function):
    @property
    def semantics(self):
        return None
    @property
    def data(self):
        return self.value
