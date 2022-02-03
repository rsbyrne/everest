###############################################################################
''''''
###############################################################################


from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    )

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.armature import Element as _Element
from everest.ptolemaic.chora import (
    Degenerate as _Degenerate,
    Chora as _Chora,
    Sampleable as _Sampleable,
    )


class Fundament(metaclass=_Bythos):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.MemberType = cls
        cls._add_mroclass('Null')
        Gen = cls._add_mroclass('Gen')
        Var = cls._add_mroclass('Var')
        cls.__class_armature_generic__ = cls.Gen(cls)
        cls.__class_armature_variable__ = cls.Var(cls)
        Oid = cls._add_mroclass('Oid')
        with Oid.mutable:
            Oid.MemberType = cls
            Oid.__armature_generic__ = property(Gen)
            Oid.__armature_variable__ = property(Var)
        cls._add_mroclass('Space', (Oid,))
        cls.__class_incision_manager__ = cls.make_class_incision_manager()


    @classmethod
    def make_class_incision_manager(cls, /):
        return cls.Space()


    class Null(metaclass=_Bythos):

        @classmethod
        def __class_incise__(cls, incisor, /, *, caller):
            if incisor is Ellipsis:
                return _IncisionProtocol.TRIVIAL(caller)()
            return _IncisionProtocol.FAIL(caller)(incisor)


    class Gen(_Element, metaclass=_Sprite):
        ...


    class Var(_Element, metaclass=_Protean):

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

        def __incise_contains__(self, arg, /) -> bool:
            return isinstance(arg, self.MemberType)

        def __incise_includes__(self, arg, /) -> bool:
            if isinstance(arg, _Degenerate):
                return arg.value in self
            try:
                return issubclass(arg.MemberType, self.MemberType)
            except AttributeError:
                return False

#         @property
#         def __incise_retrieve__(self, /):
#             return self.MemberType.__incise_retrieve__

        def __call__(self, arg, /):
            if arg in self:
                return self.__incise_retrieve__(arg)
            raise ValueError(arg)


    class Space(_Chora, metaclass=_Sprite):

        class __choret__(_Sampleable):

            def retrieve_contains(self, incisor: '.owner.MemberType', /):
                if incisor in self.bound:
                    return incisor
                raise ValueError(incisor)

            def sample_slyce_chora(self, incisor: _Chora, /):
                return incisor

        def __incise_trivial__(self, /):
            return self.owner


    @classmethod
    def __class_call__(cls, arg, /):
        return cls.__incision_manager__(arg)


###############################################################################
###############################################################################
