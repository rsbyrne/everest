###############################################################################
''''''
###############################################################################


import weakref as _weakref
import functools as _functools

from everest.incision import Incisable as _Incisable

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
        namespace['fields'] = sig.infields
        return name, bases, namespace

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    def __class_incise__(cls, incisor, /, *, caller):
        return cls.sig.__chain_incise__(incisor, caller=caller)

    def __class_incise_retrieve__(cls, params, /):
        return cls.__construct__(*params.sigargs, **params.sigkwargs)

    def __class_incise_slyce__(cls, sig, /):
        return Tektoid(cls, sig)

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

    def __call__(cls, /, *args, **kwargs):
        return cls.__incise_retrieve__(cls.sig(*args, **kwargs))


class Tektoid(_Armature, _Incisable, metaclass=_Sprite):

    incised: _Incisable
    incisor: _Incisable

    def __incise__(self, incisor, /, *, caller):
        return self.incisor.__chain_incise__(incisor, caller=caller)

    def __incise_retrieve__(self, incisor, /):
        return self.incised.__incise_retrieve__(incisor)

    def __incise_slyce__(self, incisor, /):
        return self._ptolemaic_class__(self.incised, incisor)


###############################################################################
###############################################################################
