###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import reseed as _reseed

from everest.incision import Incisable as _Incisable

from everest.ptolemaic.chora import Chora as _Chora
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.armature import Armature as _Armature


class Thing(metaclass=_Bythos):

    class Chora(_Chora):

        def retrieve_anything(self, incisor: object, /):
            return incisor

    @classmethod
    def __class_contains__(cls, arg, /):
        return True

    @classmethod
    @_abc.abstractmethod
    def __class_incise__(cls, incisor, /, *, caller):
        return cls.Chora.getmeths[type(incisor)](cls, incisor, caller=caller)

    @classmethod
    def __class_incise_generic__(cls, /):
        return GenericElement(cls, _reseed.rdigits(12))

    @classmethod
    def __class_incise_variable__(cls, /):
        return VariableElement(cls)


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
