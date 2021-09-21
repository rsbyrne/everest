###############################################################################
''''''
###############################################################################


from . import _utilities

from .pleroma import Pleromatic as _Pleromatic
from .primitive import Primitive as _Primitive


class PtolemaicBase(_Pleromatic):
    '''
    The base class of all object types
    understood by the Ptolemaic system.
    '''

_ = PtolemaicBase.register(_Primitive)


class Ptolemaic(PtolemaicBase):

    @classmethod
    def check_param(cls, arg, /):
        return isinstance(arg, PtolemaicBase)

    def __init__(self, /):
        pass

    def _repr(self, /):
        return self.params.__str__()

    @_utilities.caching.soft_cache(None)
    def __repr__(self, /):
        return f"{type(self).basecls.__name__}({self._repr()})"


###############################################################################
###############################################################################
