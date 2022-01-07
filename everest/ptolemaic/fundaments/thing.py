###############################################################################
''''''
###############################################################################


# from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.armature import (
    GenericElement as _GenericElement,
    VariableElement as _VariableElement,
    )
from everest.ptolemaic.ousia import Monument as _Monument
from everest.ptolemaic.chora import Chora as _Chora


class Thing(_Monument, _Chora):

    def slyce_chora(self, incisor: _Chora, /):
        return incisor

    def retrieve_object(self, incisor: object, /):
        return incisor

    def __incise_generic__(self, /):
        return _GenericElement(self)

    def __incise_variable__(self, /):
        return _VariableElement(self)

    def __contains__(self, arg, /):
        return True


THING = Thing()


###############################################################################
''''''
###############################################################################
