###############################################################################
''''''
###############################################################################


from . import _utilities

from .meta import PtolemaicMeta as _PtolemaicMeta


class PtolemaicBase(metaclass=_PtolemaicMeta):
    '''
    The base class of all object types
    understood by the Ptolemaic system.
    '''

    @classmethod
    def _cls_extra_init_(cls, /):
        pass

    @classmethod
    def param_checker(cls, arg):
        return isinstance(arg, PtolemaicBase)

    def __init__(self):
        pass

    def _repr(self):
        return self.params.__str__()

    @_utilities.caching.soft_cache(None)
    def __repr__(self):
        return f"{type(self).__name__}({self._repr()})"


class Primitive(metaclass=_PtolemaicMeta):
    '''
    The abstract base class of all Python types
    that are acceptables as inputs
    to the Ptolemaic system.
    '''

    PRIMITIVETYPES = (
        int,
        float,
        str,
        bytes,
        bool,
        )

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Primitive:
            if any(C is typ for typ in cls.PRIMITIVETYPES):
                return True
        return NotImplemented


_ = PtolemaicBase.register(Primitive)


###############################################################################
###############################################################################
