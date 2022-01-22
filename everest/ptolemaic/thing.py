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

from everest.ptolemaic.chora import (
    Chora as _Chora,
    Sampleable as _Sampleable,
    Degenerate as _Degenerate,
    Null as _Null,
    )
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic import armature as _armature


class ThingLike(metaclass=_Essence):
    ...


ThingLike.register(_Primitive)
ThingLike.register(_Essence)
ThingLike.register(_Ousia.BaseTyp)
ThingLike.register(_Sprite.BaseTyp)


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

    MemberType = ThingLike

    def __call__(self, arg, /):
        if arg in self:
            return arg
        raise ValueError(arg)

    def __contains__(self, arg, /) -> bool:
        return isinstance(arg, ThingLike)

    def __includes__(self, arg, /) -> bool:
        if isinstance(arg, _Degenerate):
            return arg.value in self
        try:
            return issubclass(arg.MemberType, self.MemberType)
        except AttributeError:
            return False

    __incise_generic__ = property(ThingGen)
    __incise_variable__ = property(ThingVar)


class _Thing_(_Chora, ThingSpace, metaclass=_Sprite):

    class __incision_manager__(_Sampleable):

        MemberType = ThingLike

        def retrieve_contains(self, incisor: ThingLike, /):
            return incisor

        def sample_slyce_chora(self, incisor: _Chora, /):
            return incisor

    @property
    def __incise_trivial__(self, /):
        return Thing


@ThingSpace.register
class ThingMeta(_Bythos):

    @property
    def __contains__(cls, /):
        return cls.__class_incision_manager__.__contains__

    @property
    def __includes__(cls, /):
        return cls.__class_incision_manager__.__includes__

    @property
    def __call__(cls, /):
        return cls.__class_incision_manager__.__call__

    @property
    def MemberType(cls, /):
        return cls.__class_incision_manager__.MemberType


class Thing(metaclass=ThingMeta):

    __class_incision_manager__ = _Thing_()


class _ThingNull_(_Thing_):

    class __incision_manager__:

        def retrieve_contains(self, incisor: _Null):
            pass

    @property
    def __incise_trivial__(self, /):
        return ThingNull


class ThingNull(Thing):

    __class_incision_manager__ = _ThingNull_()


###############################################################################
###############################################################################
