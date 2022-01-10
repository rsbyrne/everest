###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.incision import IncisionProtocol as _IncisionProtocol
from everest.utilities import reseed as _reseed
from everest.ptolemaic.essence import Essence as _Essence
# from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.bythos import Bythos as _Bythos
# from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic import armature as _armature


class Fundament(metaclass=_Essence):

    @classmethod
    @_abc.abstractmethod
    def __class_contains__(cls, arg, /):
        raise NotImplementedError

    @classmethod
    @_abc.abstractmethod
    def __class_incise__(cls, incisor, /, *, caller):
        raise NotImplementedError

    @classmethod
    def __class_incise_generic__(cls, /):
        return _armature.GenericElement(cls, _reseed.rdigits(12))

    @classmethod
    def __class_incise_variable__(cls, /):
        return _armature.VariableElement(cls)


class Thing(Fundament, metaclass=_Bythos):

    @classmethod
    def __class_contains__(cls, arg, /):
        return True

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        if isinstance(incisor, _IncisionProtocol):
            return incisor(caller)()
        return caller.__incise_retrieve__(incisor)


class Int(Fundament, metaclass=_Bythos):

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, int)

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        if isinstance(incisor, _IncisionProtocol):
            return incisor(caller)()
        if isinstance(incisor, int):
            return caller.__incise_retrieve__(incisor)
        return caller.__incise_fail__(incisor)


class Real(Fundament, metaclass=_Bythos):

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, float)

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        if isinstance(incisor, _IncisionProtocol):
            return incisor(caller)()
        if isinstance(incisor, float):
            return caller.__incise_retrieve__(incisor)
        return caller.__incise_fail__(incisor)


class Bool(Fundament, metaclass=_Bythos):

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, bool)

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        if isinstance(incisor, _IncisionProtocol):
            return incisor(caller)()
        if isinstance(incisor, bool):
            return caller.__incise_retrieve__(incisor)
        return caller.__incise_fail__(incisor)


class Str(Fundament, metaclass=_Bythos):

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, str)

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        if isinstance(incisor, _IncisionProtocol):
            return incisor(caller)()
        if isinstance(incisor, str):
            return caller.__incise_retrieve__(incisor)
        return caller.__incise_fail__(incisor)


class Bytes(Fundament, metaclass=_Bythos):

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, bytes)

    @classmethod
    def __class_incise__(cls, incisor, /, *, caller):
        if isinstance(incisor, _IncisionProtocol):
            return incisor(caller)()
        if isinstance(incisor, bytes):
            return caller.__incise_retrieve__(incisor)
        return caller.__incise_fail__(incisor)


###############################################################################
###############################################################################
