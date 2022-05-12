###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive

from .atlantean import Atlantean as _Atlantean
from .composite import Composite as _Composite


class Sprite(_Atlantean, _Composite):

    ...


class SpriteBase(metaclass=Sprite):

    def __process_attr__(self, val, /):
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
