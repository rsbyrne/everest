###############################################################################
''''''
###############################################################################


from everest.ptolemaic.chora import Basic as _Basic
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.armature import Armature as _Armature


class ThingLike(metaclass=_Essence):
    ...


class ThingSpace(_Basic, ThingLike, metaclass=_Essence):

    def retrieve_thing(self, incisor: object, /):
        return incisor


class Thing(ThingLike, metaclass=_Bythos):

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        return ThingSpace.__incise__(ThingSpace, incisor, caller=caller)

    @classmethod
    def __class_contains__(cls, arg, /):
        return True


class Element(_Armature):
    ...


class GenericElement(Element, metaclass=_Sprite):

    basis: object
    identity: int


class VariableElement(Element, metaclass=_Protean):

    _req_slots__ = ('_value',)
    _var_slots__ = ('value',)

    @property
    def value(self, /):
        try:
            return self._value
        except AttributeError as exc:
            raise ValueError from exc

    @value.setter
    def value(self, val, /):
        if val in self.basis:
            self._alt_setattr__('_value', val)
        elif val is None:
            self._alt_setattr__('_value', val)
        else:
            raise ValueError(val)

    @value.deleter
    def value(self, /):
        self._alt_setattr__('_value', None)


###############################################################################
###############################################################################
