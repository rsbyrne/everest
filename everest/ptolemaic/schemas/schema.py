###############################################################################
''''''
###############################################################################


from . import _Ptolemaic, _aspects
from . import _aspects


class Schema(_aspects.Singleton, _Ptolemaic):

    @classmethod
    def prekey(cls, params):
        return params.hashstr()

    def _repr(self):
        return self.params.hashstr()


###############################################################################
###############################################################################
