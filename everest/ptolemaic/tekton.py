###############################################################################
''''''
###############################################################################


import weakref as _weakref

from everest.ptolemaic.chora import Incisable as _Incisable

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.armature import Armature as _Armature
from everest.ptolemaic.params import Sig as _Sig, Params as _Params


class Tekton(_Incisable, _Essence):

    def get_signature(cls, /):
        return _Sig(cls.method)

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls.CACHE:
            cls.premade = _weakref.WeakValueDictionary()
        sig = cls.sig = cls.get_signature()

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    def method(cls, /):
        raise NotImplementedError

    @property
    def chora(cls, /):
        return cls.sig

    @property
    def retrieve(cls, /):
        return cls._cache_retrieve if cls.CACHE else cls._default_retrieve

    def _default_retrieve(cls, params, /):
        return cls.method(*params.sigargs, **params.sigkwargs)

    def _cache_retrieve(cls, params, /):
        if params in (premade := cls.premade):
            return premade[params]
        out = cls.method(*params.sigargs, **params.sigkwargs)
        premade[params] = out
        return out

    def incise(cls, chora, /):
        return TektonIncision(cls, chora)


class TektonIncision(_Incisable, metaclass=_Armature):
# class TektonIncision(metaclass=_Armature):

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
    def construct(cls, /, *args, **kwargs):
        cache = {}
        bound = cls.parameterise(cache, *args, **kwargs)
        params = _Params(cls.sig, bound)
        out = cls.retrieve(params)
        if cache:
            out.update_cache(cache)
        return out

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.construct(*args, **kwargs)


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