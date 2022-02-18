###############################################################################
''''''
###############################################################################


from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.essence import Essence as _Essence

from .chora import (
    Chora as _Chora,
    Choric as _Choric,
    Basic as _Basic,
    )
from .fundament import Fundament as _Fundament


class AllSlyce(_Fundament, metaclass=_Bythos):

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid()

    class Oid(_Choric, metaclass=_Sprite):

        def __incise_includes__(self, arg, /):
            return isinstance(arg, _Chora)

        def __incise_trivial__(self, /):
            return self._ptolemaic_class__.owner

        class __choret__(_Basic):

            def slyce_object(self, incisor: _Chora, /):
                return incisor


###############################################################################
###############################################################################
