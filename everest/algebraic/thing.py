###############################################################################
''''''
###############################################################################


from everest.primitive import Primitive as _Primitive
from everest import incision as _incision

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.essence import Essence as _Essence

from .chora import Chora as _Chora
from .choret import Basic as _Basic
from .bythos import Bythos as _Bythos
from .algebraic import Algebraic as _Algebraic
from .brace import Brace as _Brace
from .truss import Truss as _Truss


class Thing(_Algebraic, metaclass=_Bythos):


    MROCLASSES = ('Oid', 'Space', 'Brace', 'Truss')

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.Oid.register(cls)
        cls.__class_incision_manager__ = cls.Space()

    @classmethod
    def __class_call__(cls, arg, /):
        if arg in cls:
            return arg
        raise ValueError(arg)


    @_Algebraic.register
    class Oid(_Chora):

        @property
        def __armature_brace__(self, /):
            return self._ptolemaic_class__.owner.Brace.Oid

        @property
        def __armature_truss__(self, /):
            return self._ptolemaic_class__.owner.Truss.Oid

        def __incise_trivial__(self, /):
            return self

        def __includes__(self, arg, /) -> bool:
            if isinstance(arg, _incision.Degenerate):
                return arg.retrieve() in self
            owner = self._ptolemaic_class__.owner
            if arg is owner:
                return True
            return isinstance(arg, owner.Oid)

        def __contains__(self, arg, /):
            return isinstance(arg, self._ptolemaic_class__.owner)


    class Space(_Chora, metaclass=_Sprite):

        MROCLASSES = ('__incise__',)
        OVERCLASSES = ('Oid',)

        def __incise_trivial__(self, /):
            return self._ptolemaic_class__.owner

        class __incise__(_Basic):

            def retrieve_isinstance(self, incisor: 'owner.owner', /):
                return incisor

            def slyce_tuple(self, incisor: tuple, /):
                return self.bound.__armature_brace__[tuple(incisor)]


    class Brace(_Brace):

        OVERCLASSES = ('Oid',)


    class Truss(_Truss):

        OVERCLASSES = ('Oid',)


_ = Thing.register(_Primitive)
_ = Thing.register(_Essence)
# _ = Thing.register(_Ousia.BaseTyp)  # <-- Causes problems for some reason
# _ = Thing.Oid.register(_Chora)


###############################################################################
###############################################################################
