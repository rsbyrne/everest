###############################################################################
''''''
###############################################################################


from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    )

from everest.ptolemaic.chora import Choret as _Choret
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.armature import Armature as _Armature


class ThingLike(metaclass=_Essence):
    ...


class ThingSpace(_Choret, _Incisable, ThingLike):

    def __incise__(self, incisor, /, *, caller):
        if isinstance(incisor, _IncisionProtocol):
            return incisor(caller)()
        return _IncisionProtocol.RETRIEVE(caller)(incisor)


class Thing(ThingLike, metaclass=_Bythos):

    @classmethod
    def __class_get_incision_manager__(cls, /):
        return ThingSpace(cls)

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
