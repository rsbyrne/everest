###############################################################################
''''''
###############################################################################


from everest.ptolemaic.essence import Essence as _Essence

# from .algebraic import Algebraic as _Algebraic
from .chora import Chora as _Chora


class Fundament(metaclass=_Essence):


    MROCLASSES = ('Oid',)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.Oid.register(cls)


    class Oid(_Chora):

        @classmethod
        def __class_init__(cls, /):
            super().__class_init__()
            cls.register(cls.Degenerate)

        def __incise_trivial__(self, /):
            return self

        def __includes__(self, arg, /) -> bool:
            owner = self._ptolemaic_class__.owner
            if arg is owner:
                return True
            return isinstance(arg, owner.Oid)

        def __contains__(self, arg, /):
            return isinstance(arg, self._ptolemaic_class__.owner)


###############################################################################
###############################################################################
