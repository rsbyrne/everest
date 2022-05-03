###############################################################################
''''''
###############################################################################


from everest.ptolemaic.compound import Compound as _Compound

from .chora import Chora as _Chora, ChainChora as _ChainChora
from .bythos import Bythos as _Bythos
from .sig import Sig as _Sig


raise NotImplementedError


class Tekton(_Bythos):

    @classmethod
    def decorate(meta, obj, /):
        ns = dict(
            __construct__=obj,
            _clsepitaph=meta.taphonomy(obj),
            )
        return meta(obj.__name__, (), ns)

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    @property
    def __call__(cls, /):
        return cls.__incision_manager__


class TektonBase(metaclass=Tekton):


    MROCLASSES = ('Oid',)


    class Oid(_ChainChora, metaclass=_Compound):

        chora: _Chora

        @property
        def subject(self, /):
            return self._ptolemaic_class__.owner

        @property
        def __incision_manager__(self, /):
            return self.chora

        @property
        def __incise_retrieve__(self, /):
            raise NotImplementedError

        @property
        def __incise_slyce__(self, /):
            return self._ptolemaic_class__

        def __call__(self, /, *args, **kwargs):
            return self.__incise_retrieve__(self.chora(*args, **kwargs))

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.__qualname__
            self.__incision_manager__._repr_pretty_(p, cycle, root)


    @classmethod
    def _get_sig(cls, /):
        try:
            construct = cls.__construct__
        except AttributeError:
            sig = _Sig()
        else:
            sig = _Sig(construct)
        return sig

    @classmethod
    def _make_classspace(cls, /):
        return cls.Oid(cls.sig)

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.Oid.register(cls)
        cls.__class_incision_manager__ = cls._make_classspace()


###############################################################################
###############################################################################
