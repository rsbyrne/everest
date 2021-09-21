###############################################################################
''''''
###############################################################################


from . import _utilities

from .pleroma import Pleroma as _Pleroma
from .primitive import Primitive as _Primitive


class PtolemaicBase(metaclass=_Pleroma):
    '''
    The base class of all object types
    understood by the Ptolemaic system.
    '''

_ = PtolemaicBase.register(_Primitive)


class Ptolemaic(PtolemaicBase):

    @classmethod
    def _cls_extra_init_(cls, /):
        pass

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
