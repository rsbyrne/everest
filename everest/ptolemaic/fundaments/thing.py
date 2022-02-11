###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive
from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.chora import Chora as _Chora

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament
from everest.ptolemaic.fundaments.brace import Brace as _Brace


class Thing(_Fundament):


    MROCLASSES = ('Brace',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()

    @classmethod
    def __class_call__(cls, arg, /):
        return arg


    class Oid(metaclass=_Essence):

        @property
        def __armature_brace__(self, /):
            return self._ptolemaic_class__.owner.Brace


    Brace = _Brace


_ = Thing.register(_Primitive)
_ = Thing.register(_Essence)
_ = Thing.register(_Ousia.BaseTyp)
# _ = Thing.Oid.register(_Chora)


###############################################################################
###############################################################################
