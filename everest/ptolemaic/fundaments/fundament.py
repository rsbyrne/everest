###############################################################################
''''''
###############################################################################


import sys as _sys

from everest.primitive import Primitive as _Primitive
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    )

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Choric as _Choric,
    Sampleable as _Sampleable,
    )


class Fundament(metaclass=_Bythos):


    MROCLASSES = ('Oid',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid.Space()


    class Oid(_Chora, metaclass=_Essence):


        SUBCLASSES = ('Space',)

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.register(cls.Degenerate)

        # @classmethod
        # def __mroclass_init__(cls, owner, /):
        #     super().__class_init

        def __incise_includes__(self, arg, /) -> bool:
            owner = self._ptolemaic_class__.owner
            if arg is owner:
                return True
            return isinstance(arg, owner.Oid)

        def __incise_contains__(self, arg, /):
            return isinstance(arg, self._ptolemaic_class__.owner)


        class Space(_Choric, metaclass=_Sprite):

            class __choret__(_Sampleable):

                def sample_slyce_chora(self, incisor: _Chora, /):
                    if _IncisionProtocol.INCLUDES(self.bound)(incisor):
                        return incisor
                    raise ValueError(incisor)

                def retrieve_isinstance(self, incisor: 'owner.owner', /):
                    return incisor

            def __incise_trivial__(self, /):
                return self._ptolemaic_class__.owner

            def __incise_includes__(self, arg, /):
                owner = self._ptolemaic_class__.owner
                if owner is Fundament:
                    return isinstance(arg, _Chora)
                return super().__incise_includes__(arg)


# _ = Fundament.Oid.register(_Chora)


###############################################################################
###############################################################################
