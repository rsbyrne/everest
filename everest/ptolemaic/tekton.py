###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import itertools as _itertools
import weakref as _weakref
import functools as _functools
from collections import abc as _collabc

from everest.utilities import (
    caching as _caching,
    classtools as _classtools,
    )

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic import params as _params
from everest.ptolemaic import exceptions as _exceptions


class Tekton(_Essence):

    CACHE = False

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls.CACHE:
            cls.premade = _weakref.WeakValueDictionary()

    @classmethod
    def get_signature(cls, /) -> _params.Sig:
        return _params.Sig(cls.method)

    @property
    @_caching.soft_cache('_cls_softcache')
    def sig(cls, /):
        return cls.get_signature()

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    def _cache_getitem__(cls, arg, /):
        if isinstance(arg, str):
            return cls.premade[arg]
        if (hexcode := arg.hexcode) in (pre := cls.premade):
            return pre[hexcode]
        pre[hexcode] = (out := cls.construct(arg))
        return out

    @property
    def __getitem__(cls, /):
        if cls.CACHE:
            return cls._cache_getitem__
        return cls.construct


class TektonBase(metaclass=Tekton):

    @classmethod
    def method(cls, /):
        raise NotImplementedError

    @classmethod
    def construct(cls, params, /):
        return cls.method(*params.args, **params.kwargs)

    @classmethod
    def parameterise(cls, params, /, *args, **kwargs):
        params(*args, **kwargs)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        params = cls.sig.commence()
        cls.parameterise(params, *args, **kwargs)
        params.__finish__()
        return cls[params]


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