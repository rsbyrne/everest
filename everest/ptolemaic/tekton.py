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

    @classmethod
    def get_signature(meta, name, bases, namespace, /):
        try:
            construct = namespace['__construct__']
        except KeyError:
            for base in bases:
                try:
                    getattr(base, '__construct__')
                    break
                except AttributeError:
                    pass
            else:
                raise TypeError("No __construct__ method provided!")
        return _Sig(construct)

    @classmethod
    def pre_create_class(meta, /, *args):
        name, bases, namespace = super().pre_create_class(*args)
        sig = namespace['sig'] = meta.get_signature(name, bases, namespace)
        namespace['fields'] = sig.choras
        return name, bases, namespace

    @classmethod
    def __class_construct__(cls, arg0=None, /, *argn, **kwargs):
        if argn or kwargs:
            args = () if arg0 is None else (arg0, *argn)
            return super().__class_construct__(*args, **kwargs)
        return super().__class_construct__(
            name=arg.__name__,
            namespace=dict(
                __construct__=arg,
                _clsepitaph=meta.taphonomy(arg)
                ),
            )

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    def __class_get_incision_manager__(cls, /):
        return Tektoid(cls, cls.sig)

    def __call__(cls, /, *args, **kwargs):
        return _IncisionProtocol.RETRIEVE(cls)(sig(*args, **kwargs))


class Tektoid(_Armature, _ChainIncisable, metaclass=_Sprite):

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


###############################################################################
###############################################################################
