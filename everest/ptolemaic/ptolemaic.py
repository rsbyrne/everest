###############################################################################
''''''
###############################################################################


from .base import PtolemaicBase as _PtolemaicBase
from .aspect import Singleton as _Singleton


class Ptolemaic(_Singleton, _PtolemaicBase):

    @classmethod
    def prekey(cls, params):
        return params.hashstr()

    def _repr(self):
        return f"{type(self).__name__}:{self.params.hashstr()}"


###############################################################################
###############################################################################
