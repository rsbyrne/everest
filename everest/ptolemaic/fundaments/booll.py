###############################################################################
''''''
###############################################################################


from everest.ptolemaic.chora import UNIVERSE as _UNIVERSE
from everest.ptolemaic.bythos import Bythos as _Bythos


class Booll(metaclass=_Bythos):

    @classmethod
    def __incise__(cls, incisor, /, *, caller):
        return _UNIVERSE.__incise__(incisor, caller=caller)

    @classmethod
    def __incise_retrieve__(cls, incisor, /):
        if isinstance(incisor, bool):
            return incisor
        raise KeyError(incisor)

    @classmethod
    def __incise_slyce__(cls, incisor, /):
        raise NotImplementedError

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, bool)

    @classmethod
    def __class_call__(cls, arg, /):
        return bool(arg)


###############################################################################
###############################################################################
