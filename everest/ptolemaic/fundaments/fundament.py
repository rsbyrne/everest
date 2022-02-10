###############################################################################
''''''
###############################################################################


import sys as _sys

from everest.primitive import Primitive as _Primitive
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    )

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.chora import (
    Degenerate as _Degenerate,
    Chora as _Chora,
    Sampleable as _Sampleable,
    )


class Fundament(metaclass=_Bythos):


    MROCLASSES = ('Null', 'Gen', 'Var', 'Oid')

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid.Space()


    class Null(metaclass=_Bythos):

        @classmethod
        def __class_incise__(cls, incisor, /, *, caller):
            if incisor is Ellipsis:
                return _IncisionProtocol.TRIVIAL(caller)()
            return _IncisionProtocol.FAIL(caller)(incisor)


    class Gen(metaclass=_Sprite):
        ...


    class Var(metaclass=_Protean):

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


    class Oid(_IncisionHandler, metaclass=_Essence):


        SUBCLASSES = ('Space',)

        @property
        def __armature_generic__(self, /):
            return self.owner.Gen

        @property
        def __armature_variable__(self, /):
            return self.owner.Var

        def __incise_contains__(self, arg, /) -> bool:
            return arg in self.owner

        def __incise_includes__(self, arg, /) -> bool:
            if isinstance(arg, _Degenerate):
                return arg.value in self
            return _IncisionProtocol.INCLUDES(self.owner)(arg)

        def __call__(self, arg, /):
            if arg in self:
                return self.__incise_retrieve__(arg)
            raise ValueError(arg)


        class Space(_Chora, metaclass=_Sprite):

            class __choret__(_Sampleable):

                def sample_slyce_chora(self, incisor: _Chora, /):
                    if _IncisionProtocol.INCLUDES(self.bound)(incisor):
                        return incisor
                    raise ValueError(incisor)

            def __incise_trivial__(self, /):
                return self.owner

            def __incise_includes__(self, arg, /):
                if arg is (owner := self.owner):
                    return True
                return isinstance(arg, owner)

            def __incise_contains__(self, arg, /):
                return False


_ = Fundament.Oid.register(_Chora)


###############################################################################
###############################################################################
