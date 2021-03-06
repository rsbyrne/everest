################################################################################

from collections.abc import Sequence

from . import _generic
from .derived import Derived as _Derived

from .exceptions import *

class Gruple(tuple):
    def __repr__(self):
        return 'Fn' + super().__repr__()

class Group(_Derived, _generic.FuncyStruct):

    def evaluate(self):
        return Gruple(self._resolve_terms())

    def __len__(self):
        return len(self.terms)

################################################################################
