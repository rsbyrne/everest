###############################################################################
''''''
###############################################################################


from everest.ur import Dat as _Dat

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.schematic import Schematic as _Schematic

from .tekton import Tekton as _Tekton


@_Dat.register
class Eidos(_Tekton, _Schematic):

    @property
    def __call__(cls, /):
        return cls.__class_call__

    @property
    def __construct__(cls, /):
        return cls


class EidosBase(metaclass=Eidos):

    class Oid(metaclass=_Essence):

        @property
        def __incise_retrieve__(self, /):
            return self._ptolemaic_class__.owner.instantiate


###############################################################################
###############################################################################
