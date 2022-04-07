###############################################################################
''''''
###############################################################################


from everest.ptolemaic.sprite import Sprite as _Sprite

from .chora import Chora as _Chora, ChainChora as _ChainChora
from .bythos import Bythos as _Bythos
from .sig import Sig as _Sig


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


    class Oid(_ChainChora, metaclass=_Sprite):

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
            # return self._ptolemaic_class__.owner._retrieve_params
            # return cls.__construct__(*params.sigargs, **params.sigkwargs)

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


#     class ClassSlyce(_Armature, _ChainIncisable, metaclass=_Sprite):

#         subject: _Chora
#         sig: _Sig
#         subs: _Diict = _Diict()

#         @property
#         @_caching.soft_cache()
#         def __incision_manager__(self, /):
#             return _Brace[dict(
#                 sig=_Slc[::self.sig],
#                 **{key: _Slc[::sub] for key, sub in self.subs.items()},
#                 )]

#         def __incise_retrieve__(self, incisor, /):
#             return self.subject.__construct__(
#                 *incisor.sigargs, **incisor.sigkwargs
#                 )

#         def __incise_slyce__(self, incisor, /):
#             return self._ptolemaic_class__(self.subject, incisor)

#         def __call__(self, /, *args, **kwargs):
#             return self.__incise_retrieve__(self.sig(*args, **kwargs))



#     class ClassSlyce(_Armature, _ChainIncisable, metaclass=_Sprite):

#         subject: _Chora
#         chora: _Chora

#         @classmethod
#         def __class_call__(cls, subject, chora, subs=None, /):
#             if subs is not None:
#                 chora = _Brace[dict(
#                     sig=_Slc[::chora],
#                     **{key: _Slc[::sub] for key, sub in subs.items()},
#                     )]
#             inc0, *incn = chora.values()
#             if isinstance(inc0, _Degenerate):
#                 return subject.instantiate(inc0.value, incn)
#             return super().__class_call__(subject, chora)

#         @property
#         def sig(self, /):
#             return next(self.chora.values())

#         def __incision_manager__(self, /):
#             return self.chora

#         def __incise_retrieve__(self, incisor, /):
#             inc0, *incn = incisor
#             if incn:
#                 return self.subject.instantiate_retrieve(inc0, incn)
#             return self.subject.instantiate(inc0)

#         def __incise_slyce__(self, incisor, /):
#             inc0, *incn = incisor.values()
#             if isinstance(inc0, _Degenerate):
#                 return self.instantiate_slyce(inc0.value, incn)
#             return self._ptolemaic_class__(self.subject, incisor)

#         def __call__(self, /, *args, **kwargs):
#             inc0, *incn = self.chora.values()
#             params = inc0(*args, **kwargs)  # assuming inc0 is Sig type
#             if incn:
#                 return self.subject.instantiate_slyce(params, incn)
#             return self.subject.instantiate(params)
