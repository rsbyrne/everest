###############################################################################
''''''
###############################################################################


import abc as _abc

from everest import ur as _ur
from everest.primitive import Primitive as _Primitive
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    )

from everest.ptolemaic.chora import Chora as _Chora, Basic as _Basic
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic import armature as _armature


class ThingLike(metaclass=_Essence):
    ...


ThingLike.register(_Primitive)


class ThingGen(_armature.Element, ThingLike, metaclass=_Sprite):
    ...


class ThingVar(_armature.Element, ThingLike, metaclass=_Protean):

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


class ThingSpace(metaclass=_Essence):

    def __call__(self, arg, /):
        if arg in self:
            return arg
        raise ValueError(arg)

    MemberType = ThingLike

    def __contains__(self, arg, /) -> bool:
        return isinstance(arg, self.MemberType)

    __incise_generic__ = property(ThingGen)
    __incise_variable__ = property(ThingVar)


class _Thing_(_Chora, ThingSpace, metaclass=_Sprite):

    class __incision_manager__(_Basic):

        MemberType = ThingLike

        def retrieve_contains(self, incisor: '.MemberType', /):
            return incisor


class ThingMeta(_Bythos):

    __class_incision_manager__ = _Thing_()

    @property
    def __contains__(cls, /):
        return cls.__class_incision_manager__.__contains__

    @property
    def __call__(cls, /):
        return cls.__class_incision_manager__.__call__


ThingSpace.register(ThingMeta)


class Thing(metaclass=ThingMeta):
    ...


###############################################################################
###############################################################################
