###############################################################################
''''''
###############################################################################


from ..ptolemaic.essence import Essence as _Essence
from ..ptolemaic.ousia import Ousia as _Ousia
from ..ptolemaic.system import System as _System


class Algebraic(metaclass=_Essence):


    __mroclasses__ = dict(
        _Base_=(),
        Op=('_Base_',),
        Multi=('Op',),
        Variadic=('Multi',),
        )


    class _Base_(metaclass=_Ousia):

        ...


    class Op(metaclass=_Ousia):

        ...


    class Multi(metaclass=_Ousia):

        ...


    class Variadic(metaclass=_System):

        args: ARGS


    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls._Base_(*args, **kwargs)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.register(cls._Base_)


###############################################################################
###############################################################################
