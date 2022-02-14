###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive
from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Null as _Null,
    Choric as _Choric,
    Basic as _Basic,
    )

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament
from everest.ptolemaic.fundaments.brace import Brace as _Brace


class Thing(_Fundament, metaclass=_Bythos):


    MROCLASSES = ('Brace',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid.Space()

    @classmethod
    def __class_call__(cls, arg, /):
        return arg


    class Oid(metaclass=_Essence):

        SUBCLASSES = ('Space',)

        @property
        def __armature_brace__(self, /):
            return self._ptolemaic_class__.owner.Brace

        class Space(_Choric, metaclass=_Sprite):

            def __incise_trivial__(self, /):
                return self._ptolemaic_class__.owner

            class __choret__(_Basic, metaclass=_Essence):

                def retrieve_isinstance(self, incisor: 'owner.owner', /):
                    return incisor


    Brace = _Brace


_ = Thing.register(_Primitive)
_ = Thing.register(_Essence)
_ = Thing.register(_Ousia.BaseTyp)
# _ = Thing.Oid.register(_Chora)


###############################################################################
###############################################################################
