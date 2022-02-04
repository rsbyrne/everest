###############################################################################
''''''
###############################################################################


import weakref as _weakref
import functools as _functools

from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
#     Incisable as _Incisable,
    ChainIncisable as _ChainIncisable,
    )

from everest.ptolemaic.chora import Chora as _Chora
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.sig import Sig as _Sig
from everest.ptolemaic.armature import Armature as _Armature
from everest.ptolemaic.sprite import Sprite as _Sprite


class Tekton(_Bythos):

    @property
    def __class_incision_manager__(cls, /):
        return cls.Slyce(cls, cls.sig)

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

    MROCLASSES = ('Slyce',)

    class Slyce(_Armature, _ChainIncisable, metaclass=_Sprite):

        subject: _Chora
        sig: _Chora

        @property
        def __incision_manager__(self, /):
            return self.sig

        def __incise_retrieve__(self, incisor, /):
            return self.subject.__construct__(
                *incisor.sigargs, **incisor.sigkwargs
                )

        def __incise_slyce__(self, incisor, /):
            return self._ptolemaic_class__(self.subject, incisor)

        def __call__(self, /, *args, **kwargs):
            return self.__incise_retrieve__(self.sig(*args, **kwargs))

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        try:
            construct = cls.__construct__
        except AttributeError:
            sig = _Sig()
        else:
            sig = _Sig(construct)
        cls.sig = sig
        cls.fields = sig.sigfields

#     @classmethod
#     def __construct__(cls, /):
#         raise NotImplementedError


###############################################################################
###############################################################################
