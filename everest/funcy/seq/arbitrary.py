################################################################################

from .seq import Seq as _Seq

class Arbitrary(_Seq):
    discrete = True
    def _iter(self):
        return self._resolve_terms()
    def _seqLength(self):
        return len(self.terms)

class SettableArbitrary(Arbitrary):
    def __setitem__(self, index, value):
        self.update()
        self.refresh()
        self.terms[index] = value

################################################################################
