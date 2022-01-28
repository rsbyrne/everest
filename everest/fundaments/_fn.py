###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.chora import Chora as _Chora, Basic as _Basic
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.thing import Thing as _Thing
from everest.ptolemaic.tuuple import Tuuple as _Tuuple
from everest.ptolemaic.intt import Intt as _Intt
# from everest.ptolemaic.floatt import Floatt as _Floatt
# from everest.ptolemaic.booll import Booll as _Booll
# from everest.ptolemaic.strr import Strr as _Strr


_ALIASES = {
    object: _Thing,
    tuple: _Tuuple,
    int: _Intt,
#     float: _Floatt,
#     bool: _Booll,
#     str: _Strr,
    }


class _Fn_(_Chora, metaclass=_Sprite):

    class Choret(_Basic):

        def retrieve_type(self, incisor: type, /):
            return _ALIASES[incisor]

        def retrieve_primitive(self, incisor: _Primitive, /):
            return incisor


class FnMeta(_Bythos):

    __incision_manager__ = _Fn_()


class Fn(metaclass=FnMeta):

    @classmethod
    def __init_subclass__(cls, /, *args, **kwargs):
        raise TypeError("This type cannot be subclassed.")


###############################################################################
###############################################################################
