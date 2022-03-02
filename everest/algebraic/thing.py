###############################################################################
''''''
###############################################################################


# from collections import abc as _collabc

from everest.primitive import Primitive as _Primitive
from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.essence import Essence as _Essence

from .chora import (
    Chora as _Chora,
    Null as _Null,
    Choric as _Choric,
    Basic as _Basic,
    )
from .armature import ArmatureProtocol as _ArmatureProtocol
from .fundament import Fundament as _Fundament
from .brace import Brace as _Brace


class Thing(_Fundament, metaclass=_Bythos):


    # MROCLASSES = ('Brace',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid.Space()

    @classmethod
    def __class_call__(cls, arg, /):
        if arg in cls:
            return arg
        raise ValueError(arg)


    class Oid(metaclass=_Essence):

        SUBCLASSES = ('Space', 'Brace')

        @property
        def __armature_brace__(self, /):
            return self._ptolemaic_class__.owner.Oid.Brace
            # try:
            #     self._ptolemaic_class__.__dict__['Brace']
            # except KeyError:
            #     raise AttributeError

        class Space(_Choric, metaclass=_Sprite):

            def __incise_trivial__(self, /):
                return self._ptolemaic_class__.owner

            class __choret__(_Basic, metaclass=_Essence):

                def retrieve_isinstance(self, incisor: 'owner.owner', /):
                    return incisor

                def slyce_tuple(self, incisor: tuple, /):
                    return _ArmatureProtocol.BRACE(self.bound)[
                        tuple(incisor)
                        ]


        Brace = _Brace


_ = Thing.register(_Primitive)
_ = Thing.register(_Essence)
_ = Thing.register(_Ousia.BaseTyp)
# _ = Thing.Oid.register(_Chora)


###############################################################################
###############################################################################
