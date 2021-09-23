###############################################################################
''''''
###############################################################################


from . import _Ptolemaic
from . import _behaviours


class Schema(_behaviours.Singleton, _Ptolemaic):

    @classmethod
    def prekey(cls, params):
        return params.hashID

    def _repr(self):
        return self.params.hashID


###############################################################################
###############################################################################
