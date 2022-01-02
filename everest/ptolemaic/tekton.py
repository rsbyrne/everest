###############################################################################
''''''
###############################################################################


import weakref as _weakref
import functools as _functools

from everest.ptolemaic import chora as _chora

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.armature import Armature as _Armature
from everest.ptolemaic.sig import Sig as _Sig, Params as _Params


class Tekton(_Essence):

    def __construct__(cls, /):
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

    def incise(cls, chora, /):
        return TektonIncision(cls, chora)

    def trivial(cls, /):
        return cls

    @property
    def fail(cls, /):
        return _functools.partial(_chora.Incisable.fail, cls)

    @property
    def __getitem__(cls, /):
        return _functools.partial(_chora.Incisable.__getitem__, cls)

    @classmethod
    def decorate(meta, arg, /):
        return meta(
            name=arg.__name__,
            namespace=dict(
                __construct__=arg,
                _clsepitaph=meta.metataphonomy(arg)
                ),
            )


class TektonIncision(_chora.Incisable, metaclass=_Armature):

    tekton: Tekton
    sig: _Sig

    @property
    def chora(self, /):
        return self.sig

    @property
    def retrieve(self, /):
        return self.tekton.retrieve

    def incise(self, chora, /):
        return TektonIncision(self.tekton, chora)

    @property
    def __signature__(self, /):
        return self.sig.signature

    def __call__(self, /, *args, **kwargs):
        return self.retrieve(self.sig(*args, **kwargs))


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


# class BadParameters(_exceptions.ParameterisationException):

#     def __init__(self, owner: type, bads: tuple, /):
#         self.bads = bads
#         super().__init__(owner)

#     def message(self, /):
#         yield from super().message()
#         yield "when one or more parameters failed the prescribed check:"
#         for param in self.bads:
#             yield f"{repr(param)}, {repr(type(param))}"


# class Registrar:
#     '''
#     Handles parameterisation and type checking
#     on behalf of its outer class.
#     '''

#     __slots__ = ('_owner', 'args', 'kwargs')

#     def __init__(self, owner: type, /):
#         self._owner, self.args, self.kwargs = \
#             _weakref.ref(owner), [], {}

#     ### Basic functionality to check and process parameters:

#     @property
#     def owner(self, /):
#         return self._owner()

#     @property
#     def process_param(self, /):
#         return self.owner.process_param

#     @property
#     def check_param(self, /):
#         return self.owner.check_param

#     def __call__(self, /, *args, **kwargs):
#         self.args.extend(map(self.process_param, args))
#         self.kwargs.update(zip(
#             map(str, kwargs),
#             map(self.process_param, kwargs.values())
#             ))

#     def finalise(self, /):
#         callsig = CallSig.signature_call(
#             self.owner.__signature__,
#             self.args,
#             self.kwargs,
#             )
#         if bads := tuple(_itertools.filterfalse(
#                 self.check_param,
#                 callsig.values(),
#                 )):
#             raise BadParameters(self.owner, bads)
#         return callsig

#     ### Basic object legibility:

#     def _repr(self, /):
#         argtup = ', '.join(map(repr, self.args))
#         kwargtup = ', '.join(
#             f"{key}: {repr(val)}"
#             for key, val in self.kwargs.items()
#             )
#         return f"*({argtup}), **{{{kwargtup}}}"