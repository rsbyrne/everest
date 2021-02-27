################################################################################

from .derived import Derived

class UnSeq(Derived):

    def __init__(self, seq, **kwargs):
        super().__init__(seq, **kwargs)

    def evaluate(self):
        return list(self.prime.value)

################################################################################
