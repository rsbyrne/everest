################################################################################

from . import _generic
from .derived import Derived as _Derived

from .exceptions import *

class Slyce(_Derived, _generic.FuncySlice):

    def __init__(self, arg1, arg2 = None, arg3 = None, /, **kwargs):
        super().__init__(arg1, arg2, arg3)

    def evaluate(self):
        return slice(*self.terms)

################################################################################