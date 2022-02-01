###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    IncisionHandler as _IncisionHandler,
    )

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic import armature as _armature
from everest.ptolemaic.chora import (
    Degenerate as _Degenerate,
    Chora as _Chora,
    Basic as _Basic,
    Sampleable as _Sampleable,
    Null as _Null,
    )


class Thing(metaclass=_Bythos):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.MemberType = cls
        cls._add_mroclass('Null')
        cls._add_mroclass('Gen')
        cls._add_mroclass('Var')
        cls.__class_armature_generic__ = cls.Gen(cls)
        cls.__class_armature_variable__ = cls.Var(cls)
        Oid = cls._add_mroclass('Oid')
        cls._add_mroclass('Space', (Oid,))
        cls.__class_incision_manager__ = cls.Space()


    class Null(metaclass=_Bythos):

        @classmethod
        def __class_incise__(cls, incisor, /, *, caller):
            if incisor is Ellipsis:
                return _IncisionProtocol.TRIVIAL(caller)()
            return _IncisionProtocol.FAIL(caller)(incisor)


    class Gen(_armature.Element, metaclass=_Sprite):
        ...


    class Var(_armature.Element, metaclass=_Protean):

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

        @classmethod
        def __class_init__(cls, /):
            if 'owner' in cls.__dict__:
                cls.MemberType = cls.owner.MemberType
                cls.__armature_generic__ = property(cls.owner.Gen)
                cls.__armature_variable__ = property(cls.owner.Var)
            super().__class_init__()

        def __call__(self, arg, /):
            if arg in self:
                return arg
            raise ValueError(arg)

        def __incise_contains__(self, arg, /) -> bool:
            return isinstance(arg, self.MemberType)

        def __incise_includes__(self, arg, /) -> bool:
            if isinstance(arg, _Degenerate):
                return arg.value in self
            try:
                return issubclass(arg.MemberType, self.MemberType)
            except AttributeError:
                return False

        @classmethod
        def __instancecheck__(cls, other, /):
            owner = cls.owner
            if cls is owner.Oid:
                if other is owner:
                    return True
            return super().__instancecheck__(other)


    class Space(_Chora, metaclass=_Sprite):

        class __choret__(_Sampleable):

            MemberType = _Null

            @classmethod
            def __class_init__(cls, /):
                try:
                    cls.MemberType = cls.owner.MemberType
                except AttributeError:
                    pass
                super().__class_init__()

            def retrieve_contains(self, incisor: '.MemberType', /):
                return incisor

            def sample_slyce_chora(self, incisor: _Chora, /):
                return incisor

        def __incise_trivial__(self, /):
            return self.owner


    @classmethod
    def __class_call__(cls, arg, /):
        return cls.__incision_manager__(arg)


_ = Thing.register(_Primitive)
_ = Thing.register(_Essence)
_ = Thing.register(_Ousia.BaseTyp)
_ = Thing.register(_Sprite.BaseTyp)


###############################################################################
###############################################################################
