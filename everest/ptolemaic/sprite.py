###############################################################################
''''''
###############################################################################


from everest.armature import Armature as _Armature

from . import ptolemaic as _ptolemaic


@_ptolemaic.Ptolemaic.register
class Sprite(_Armature):

    @property
    def param_convert(cls, /):
        return _ptolemaic.convert


@_ptolemaic.Ptolemaic.register
class _SpriteBase_(_Armature.BaseTyp):

    __req_slots__ = ('__corpus__', '__relname__')

    @classmethod
    def _construct_(cls, params: tuple, /):
        obj = cls._instantiate_(params)
        obj.__corpus__ = None
        obj.__relname__ = None
        obj.initialise()
        return obj

    @classmethod
    def semi_call(cls, *args, **kwargs):
        return cls.instantiate(tuple(
            cls.parameterise(*args, **kwargs)
            .__dict__.values()
            ))

    def __set_name__(self, owner, name, /):
        if self.mutable:
            try:
                name = owner.__unmangled_names__[name]
            except (AttributeError, KeyError):
                pass
            self.__corpus__ = owner
            self.__relname__ = name
            self.initialise()
            owner.register_organ(self)

    @property
    def __cosmic__(self, /):
        return self.__corpus__ is None


Sprite.BaseTyp = _SpriteBase_


###############################################################################
###############################################################################
