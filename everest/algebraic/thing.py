###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.essence import Essence as _Essence

from .chora import (
    Choric as _Choric,
    Basic as _Basic,
    )
from .armature import ArmatureProtocol as _ArmatureProtocol
from .fundament import Fundament as _Fundament
from .brace import Brace as _Brace
from .truss import Truss as _Truss


class Thing(_Fundament, metaclass=_Bythos):


    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__class_incision_manager__ = cls.Oid.Space()

    @classmethod
    def __class_call__(cls, arg, /):
        if arg in cls:
            return arg
        raise ValueError(arg)


    class Oid(metaclass=_Essence):

        SUBCLASSES = ('Space', 'Brace', 'Truss')

        Brace = _Brace
        Truss = _Truss

        @property
        def __armature_brace__(self, /):
            return self._ptolemaic_class__.owner.Oid.Brace

        @property
        def __armature_truss__(self, /):
            return self._ptolemaic_class__.owner.Oid.Truss

        class Space(_Choric, metaclass=_Sprite):

            def __incise_trivial__(self, /):
                return self._ptolemaic_class__.owner

            class __choret__(_Basic, metaclass=_Essence):

                def retrieve_isinstance(self, incisor: 'owner.owner', /):
                    return incisor

                def slyce_tuple(self, incisor: tuple, /):
                    return _ArmatureProtocol.BRACE(self.bound)[
                        tuple(incisor)
                        ]

        def __truediv__(self, arg, /):
            return _Brace[self.__incise_trivial__(), arg]

        def __rtruediv__(self, arg, /):
            return _Brace[arg, self.__incise_trivial__()]

        def __floordiv__(self, arg, /):
            return NotImplemented

        def __rfloordiv__(self, arg, /):
            return NotImplemented

        def __mod__(self, arg, /):
            return _Brace.Oid.SymForm(self.__incise_trivial__(), arg)

        def __rmod__(self, arg, /):
            return NotImplemented

        def __matmul__(self, arg, /):
            return NotImplemented

        def __rmatmul__(self, arg, /):
            return NotImplemented


    for methname in ('truediv', 'floordiv', 'mod', 'matmul'):
        for prefix in ('', 'r'):
            exec('\n'.join((
                f"@classmethod",
                f"def __class_{prefix}{methname}__(cls, /, *args, **kwargs):",
                (f"    return cls.__class_incision_manager__"
                     f".__{prefix}{methname}__(*args, **kwargs)"),
                )))
    del methname, prefix


_ = Thing.register(_Primitive)
_ = Thing.register(_Essence)
_ = Thing.register(_Ousia.BaseTyp)
# _ = Thing.Oid.register(_Chora)


###############################################################################
###############################################################################
