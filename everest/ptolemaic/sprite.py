###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive

from .ousia import Ousia as _Ousia
from .composite import Composite as _Composite


class Sprite(_Ousia, _Composite):

    ...


class SpriteBase(metaclass=Sprite):

    @classmethod
    def __process_field__(cls, val, /):
        if isinstance(val, _Primitive):
            return val
        raise TypeError(
            "Only Primitive types are permitted as attributes of Sprites."
            )

    @classmethod
    def __class_call__(cls, /, *args):
        return cls.instantiate(args)


###############################################################################
###############################################################################
