###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import functools as _functools
import types as _types
import collections.abc as _collabc
from enum import Enum as _Enum

from everest.utilities import (
    caching as _caching,
    classtools as _classtools,
    format_argskwargs as _format_argskwargs,
    )

from everest import epitaph as _epitaph
from everest.ptolemaic.chora import (
    Incisable as _Incisable,
    Degenerate as _Degenerate,
    Chora as _Chora,
    MultiMapp as _MultiMapp,
    DEFAULTCALLER as _DEFAULTCALLER
    )
from everest.ptolemaic.armature import Armature as _Armature

_pkind = _inspect._ParameterKind
_pempty = _inspect._empty

_mprox = _types.MappingProxyType


class _GENERICCLASS_(_Chora):

    def compose(self, other, /):
        return other

    def retrieve_object(self, incisor: object, /):
        return incisor

    def __repr__(self, /):
        return 'GENERIC'


GENERIC = _GENERICCLASS_()


class ParamKind(_Enum):

    Pos = _pkind['POSITIONAL_ONLY']
    PosKw = _pkind['POSITIONAL_OR_KEYWORD']
    Args = _pkind['VAR_POSITIONAL']
    Kw = _pkind['KEYWORD_ONLY']
    Kwargs = _pkind['VAR_KEYWORD']

    def __repr__(self, /):
        return f"ParamKind[{self.name}]"

    @property
    def epitaph(self, /):
        try:
            return self._epitaph
        except AttributeError:
            epi = self._epitaph = _epitaph.TAPHONOMY.custom_epitaph(
                "$A[$a]", A=ParamKind, a=self.name
                )
            return epi

    @classmethod
    def convert(cls, arg, /):
        if isinstance(arg, cls):
            return arg
        if isinstance(arg, str):
            return cls[arg]
        if isinstance(arg, _pkind):
            return tuple(cls)[arg.value]
        raise TypeError("Cannot convert to `ParamKind`.")

    @property
    def score(self, /):
        return self.value.value


class ParamMeta(_Armature):

    for kind in ParamKind:
        exec('\n'.join((
            '@property',
            f'def {kind.name}(cls, /):'
            f"    return cls(ParamKind.{kind.name})"
            )))


class Param(_Incisable, metaclass=ParamMeta):

    kind: str = ParamKind.Pos
    hint: type = GENERIC
    value: object = NotImplemented

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        kind, hint, value = bound.arguments.values()
        bound.arguments.update(
            kind=(ParamKind.convert(kind) if isinstance(kind, _pkind) else kind),
            hint=(GENERIC if hint is _pempty else hint),
            value=(NotImplemented if value is _pempty else value),
            )
        return bound

    def get_parameter(self, name: str = 'anon', /):
        default = _pempty if (val:=self.value) is NotImplemented else val
        return _inspect.Parameter(
            name, self.kind.value,
            default=default,
            annotation=self.hint,
            )

    def __call__(self, value, /):
        return self.__class_call__(self.kind, self.hint, value)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls(hint=arg)

    def retrieve(self, index, /):
        return self.incise(_Degenerate(index))

    def incise(self, chora, /):
        return self.__class_call__(self.kind, chora, self.value)

    @property
    def chora(self, /):
        return self.hint

    def __getitem__(self, arg, /):
        if isinstance(arg, Param):
            return self.__class_call__(
                max(param.kind for param in (self, incisor)),
                self.hint[incisor.hint],
                (self.value if (val := incisor.value) is NotImplemented else val),
                )
        elif isinstance(arg, _Degenerate):
            return self.incise(arg)
        return super().__getitem__(arg)


class Sig(_Incisable, metaclass=_Armature):

    FIELDS = (
        _inspect.Parameter('_basesig', 3, default=None),
        _inspect.Parameter('params', 4),
        )

    @staticmethod
    def _get_orderscore(pair):
        _, obj = pair
        if isinstance(obj, _Degenerate):
            return -1
        adj = 0 if obj.value is NotImplemented else 0.5
        return obj.kind.score + adj

    @classmethod
    def parameterise(cls,
            cache, arg=None, /,
            _chora=None, _basesig=None, **params,
            ):
        if arg is None:
            params = dict(sorted(
                params.items(),
                key=cls._get_orderscore,
                ))
        elif params:
            raise RuntimeError(
                f"Must provide exactly one of either arg or params "
                f"to {self.__class__._ptolemaic_class__}."
                )
        else:
            if isinstance(arg, _inspect.Signature):
                signature = arg
            else:
                signature = _inspect.signature(arg)
            cache['signature'] = signature
            params = {
                pm.name: Param(pm.kind, pm.annotation, pm.default)
                for pm in signature.parameters.values()
                }
        if _chora is not None:
            cache['chora'] = _chora
        return super().parameterise(cache, _basesig=_basesig, **params)

    @property
    @_caching.soft_cache()
    def degenerates(self, /):
        return _mprox({
            name: param.hint.value
            for name, param in self.params.items()
            if isinstance(param.hint, _Degenerate)
            })

    @property
    def basesig(self, /):
        return self if (basesig := self._basesig) is None else basesig

    @property
    @_caching.soft_cache()
    def signature(self, /):
        return _inspect.Signature(
            param.get_parameter(name) for name, param in self.params.items()
            if not isinstance(param.hint, _Degenerate)
            )

    def bind(self, /, *args, **kwargs):
        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @property
    @_caching.soft_cache()
    def chora(self, /):
        return _MultiMapp(**{key: val.hint for key, val in self.params.items()})

    def incise(self, chora, /):
        params = {
            key: Param(param.kind, cho, param.value)
            for ((key, param), cho) in zip(self.params.items(), chora.choras)
            }
        return self.__class_call__(_chora=chora, _basesig=self.basesig, **params)

    def retrieve(self, index: dict, /):
        return Params(self, index)

    def __call__(self, /, *args, **kwargs):
        return self.retrieve({
            **self.bind(*args, **kwargs).arguments,
            **self.degenerates,
            })

    def __str__(self, /):
        return str(self.signature)


# DEFAULTSIG = Sig(args=Param.Args, kwargs=Param.Kwargs)

@_classtools.add_defer_meths('content', like=dict)
class Params(metaclass=_Armature):

    FIELDS = (
        _inspect.Parameter('sig', 0, annotation=Sig),
        _inspect.Parameter('content', 0, annotation=dict),
        )

    @classmethod
    def parameterise(cls, cache, arg0, arg1=None, /, **kwargs):
        if not isinstance(arg0, Sig):
            arg0 = Sig(arg0)
        arg0 = arg0.basesig
        if arg1 is None:
            arg1 = kwargs
        elif kwargs:
            raise ValueError("Cannot pass kwargs if two args are passed.")
        elif isinstance(arg1, _inspect.BoundArguments):
            cache['bound'] = arg1
            arg1 = arg1.arguments
        elif isinstance(arg1, _collabc.Mapping):
            pass
        else:
            raise TypeError("Input for `arg1` not recognised.")
        return super().parameterise(cache, arg0, arg1)

    @property
    @_caching.soft_cache()
    def bound(self, /):
        bound = self.sig.signature.bind_partial()
        bound.apply_defaults()
        bound.arguments.update(self.content)
        return bound

    @property
    def sigargs(self, /):
        return self.bound.args

    @property
    def sigkwargs(self, /):
        return _mprox(self.bound.kwargs)


class ParamProp:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        self.name = name

    def __get__(self, instance, _=None):
        return instance.params[self.name]


# class Params(_Ptolemaic):

#     __slots__ = (
#         'signature', '_args', '_kwargs', 'args', 'kwargs',
#         'arguments', '_getmeths', '_setmeths',
#         )

#     def __init__(self, signature=DEFAULTSIG, /, *args, **kwargs):
#         super().__init__()
#         self.signature = signature
#         args = self._args = list(args)
#         self._kwargs = kwargs
#         self.kwargs = _types.MappingProxyType(kwargs)
#         self._getmeths = {int: args.__getitem__, str: kwargs.__getitem__}
#         self._setmeths = {int: args.__setitem__, str: kwargs.__setitem__}

#     def __finish__(self, /):
#         args, kwargs = self._args, self._kwargs
#         bound = self.signature.bind(*args, **kwargs)
#         bound.apply_defaults()
#         args[:] = bound.args
#         kwargs.update(bound.kwargs)
#         self.args = tuple(args)
#         self.arguments = _types.MappingProxyType(bound.arguments)
#         super().__finish__()

#     def __getitem__(self, arg, /):
#         if self.finalised:
#             return self.arguments[arg]
#         return self._getmeths[type(arg)](arg)

#     def __setitem__(self, arg, val, /):
#         if self.finalised:
#             raise RuntimeError("This object has been finalised.")
#         return self._setmeths[type(arg)](arg, val)

#     def __call__(self, /, *args, **kwargs):
#         if self.finalised:
#             raise RuntimeError("This object has been finalised.")
#         self._args.extend(args)
#         self._kwargs.update(kwargs)

#     def get_epitaph(self, /):
#         return self.taphonomy.callsig_epitaph(
#             self.__class__._ptolemaic_class__,
#             self.signature, *self._args, **self._kwargs,
#             )

#     def __str__(self, /):
#         return _format_argskwargs(*self.args, **self.kwargs)

#     def _repr(self, /):
#         return f"{repr(self.signature)}, {str(self)}"


###############################################################################
###############################################################################

