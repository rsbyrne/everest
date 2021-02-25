################################################################################

from collections.abc import Sequence

from .exceptions import *
from .derived import Derived
from .base import Function
from .ops import ops

class Gruple(tuple):
    def __repr__(self):
        return 'Fn' + super().__repr__()

class Group(Derived, Sequence):

    def evaluate(self):
        return Gruple(self._resolve_terms())
    def __getitem__(self, index):
        return ops.getitem(self, index)
    def __len__(self):
        return len(self.terms)
    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

################################################################################
