###############################################################################
''''''
###############################################################################


import weakref as _weakref
import functools as _functools

from everest.ptolemaic import chora as _chora

from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.armature import Armature as _Armature
from everest.ptolemaic.sig import Sig as _Sig, Params as _Params


class Tekton(_Bythos):

    @staticmethod
    def __construct__():
        raise NotImplementedError

    @classmethod
    def get_signature(meta, name, bases, namespace, /):
        return _Sig(namespace.get('__construct__', meta.__construct__))

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):
        super().pre_create_class(name, bases, namespace)
        namespace['sig'] = meta.get_signature(name, bases, namespace)

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls.CACHE:
            cls.premade = _weakref.WeakValueDictionary()

    @property
    def chora(cls, /):
        return cls.sig

    def retrieve(cls, params, /):
        if cls.CACHE:
            if params in (premade := cls.premade):
                return premade[params]
            out = cls.construct(params)
            premade[params] = out
        else:
            print(cls, params)
            out = cls.construct(params)
        return out

    def __class_call__(cls, /, *args, **kwargs):
        cache = {}
        bound = cls.parameterise(cache, *args, **kwargs)
        params = _Params(bound)
        out = cls.retrieve(params)
        if cache:
            out.update_cache(cache)
        return out

    @classmethod
    def decorate(meta, arg, /):
        return meta(
            name=arg.__name__,
            namespace=dict(
                __construct__=arg,
                _clsepitaph=meta.metataphonomy(arg)
                ),
            )


class TektonBase(metaclass=Tekton):

    CACHE = False

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @classmethod
    def construct(cls, params, /):
        return cls.__construct__(*params.sigargs, **params.sigkwargs)


###############################################################################
###############################################################################


# class TektonIncision(_chora.Incision):

#     tekton: Tekton
#     sig: _Sig

#     @property
#     def chora(self, /):
#         return self.sig

#     @property
#     def retrieve(self, /):
#         return self.tekton.retrieve

#     def incise(self, chora, /):
#         return TektonIncision(self.tekton, chora)

#     @property
#     def __signature__(self, /):
#         return self.sig.signature

#     def __call__(self, /, *args, **kwargs):
#         return self.retrieve(self.chora(*args, **kwargs))

