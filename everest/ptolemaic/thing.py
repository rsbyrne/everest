###############################################################################
''''''
###############################################################################


from everest import ur as _ur
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    )

from everest.ptolemaic.chora import Basic as _Basic
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic import armature as _armature


class ThingLike(metaclass=_Essence):
    ...


class ThingElement(_armature.Element, ThingLike):
    ...


class ThingGeneric(ThingElement, metaclass=_Sprite):
    ...


class ThingVar(ThingElement, metaclass=_Protean):

    _req_slots__ = ('_value',)
    _var_slots__ = ('value',)

    _default = None

    @property
    def value(self, /):
        try:
            return self._value
        except AttributeError:
            val = self._default
            self._alt_setattr__('_value', val)
            return val

    @value.setter
    def value(self, val, /):
        if val not in self.basis:
            raise ValueError(val)
        self._alt_setattr__('_value', val)

    @value.deleter
    def value(self, /):
        self._alt_setattr__('_value', self._default)


class ThingSpace(_Basic, _Incisable, ThingLike):

    @property
    def __incise_generic__(self, /):
        return ThingGeneric(self.bound)

    @property
    def __incise_variable__(self, /):
        return ThingVar(self.bound)

    def retrieve_contains(self, incisor: object, /):
        return incisor

    @property
    def __contains__(self, /):
        return self.bound.__contains__


class Thing(ThingLike, metaclass=_Bythos):

    @classmethod
    def __class_get_incision_manager__(cls, /):
        return ThingSpace(cls)

    @classmethod
    def __class_contains__(cls, arg, /):
        return True


###############################################################################
###############################################################################
