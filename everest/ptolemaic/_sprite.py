###############################################################################
''''''
###############################################################################


from everest.armature import Armature as _Armature

from . import ptolemaic as _ptolemaic
from .utilities import get_ligatures as _get_ligatures


@_ptolemaic.Theme.register
class SpriteMeta(type):
    ...


@_ptolemaic.Kind.register
class Sprite(_Armature, metaclass=SpriteMeta):

    @property
    def param_convert(cls, /):
        return _ptolemaic.convert

    @classmethod
    def _get_merged_slots(meta, bases, ns, params, /):
        return _ptolemaic.convert(super()._get_merged_slots(
            bases, ns, params
            ))


@_ptolemaic.Case.register
class _SpriteBase_(_Armature.BaseTyp):

    __req_slots__ = ('__corpus__', '__relname__')
    __slots__ = ()

    @classmethod
    def _construct_(cls, params: tuple, /):
        obj = cls._instantiate_(params)
        obj.__corpus__ = None
        obj.__relname__ = None
        obj.initialise()
        return obj

    def __set_name__(self, owner, name, /):
        if self.mutable:
            self.__corpus__ = owner
            self.__relname__ = name
            self.initialise()

    @property
    def __cosmic__(self, /):
        return self.__corpus__ is None

    @classmethod
    def __prop_get__(cls, instance, name, /):
        return cls[
            tuple(_get_ligatures(cls, instance).arguments.values())
            ]

    @classmethod
    def __organ_get__(cls, instance, name, /):
        out = cls.instantiate(
            tuple(_get_ligatures(cls, instance).arguments.values())
            )
        out.__set_name__(instance, name)
        return out

    def __repr__(self, /):
        if self.__cosmic__:
            return super().__repr__()
        return f"{self.__corpus__}.{self.__relname__}"


###############################################################################
###############################################################################
