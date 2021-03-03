################################################################################

from .derived import Derived as _Derived

class UnSeq(_Derived):

    def __init__(self, seq, **kwargs):
        super().__init__(seq, **kwargs)

    def evaluate(self):
        return list(self.prime.value)

################################################################################
