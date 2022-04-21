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
        ...
        # @classmethod
        # def __class_init__(cls, /):
        #     super().__class_init__()
        #     cls.register(cls.Degenerate)


###############################################################################
###############################################################################
