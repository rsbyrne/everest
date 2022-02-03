###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.essence import Essence as _Essence

from everest.ptolemaic.fundaments.fundament import Fundament as _Fundament
from everest.ptolemaic.fundaments.brace import Brace as _Brace


class Thing(_Fundament):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Brace = cls._add_mroclass('Brace', (_Brace,))
        cls.__class_armature_brace__ = cls.Brace

    @classmethod
    def __class_incise_retrieve__(cls, arg, /):
        return arg


    class Brace(_Brace):

        @classmethod
        def __class_init__(cls, /):
            try:
                owner = cls.owner
            except AttributeError:
                pass
            else:
                super().__class_init__()
                cls.SubmemberType = owner

        @classmethod
        def __class_incise_retrieve__(cls, arg, /):
            return arg


_ = Thing.register(_Primitive)
_ = Thing.register(_Essence)
_ = Thing.register(_Ousia.BaseTyp)
_ = Thing.register(_Sprite.BaseTyp)


###############################################################################
###############################################################################
