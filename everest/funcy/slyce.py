################################################################################

from .derived import Derived as _Derived

class Slyce(_Derived):

    def __init__(self, arg1, arg2 = None, arg3 = None, /, **kwargs):
        super().__init__(arg1, arg2, arg3)

    def evaluate(self):
        return slice(*self.terms)

################################################################################