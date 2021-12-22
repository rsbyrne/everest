###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools
import types as _types

from everest.utilities import (
    caching as _caching,
    classtools as _classtools,
    format_argskwargs as _format_argskwargs,
    )

from everest.incision import (
    Incisable as _Incisable,
    IncisableHost as _IncisableHost,
    Degenerate as _Degenerate,
    DEFAULTCALLER as _DEFAULTCALLER
    )
from everest.ptolemaic.armature import Armature as _Armature
from everest.ptolemaic.chora import MultiMapp as _MultiMapp

_pkind = _inspect._ParameterKind
_pempty = _inspect._empty

_mprox = _types.MappingProxyType


KINDNAMES = ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs')
KINDS = dict(zip(KINDNAMES, _pkind))


class GENERIC:

    @classmethod
    def __class_getitem__(cls, arg, /):
        if isinstance(arg, _Incisable):
            return arg
        raise TypeError(type(arg))

    @classmethod
    def getitem(cls, arg, /, *, caller=_DEFAULTCALLER):
        return caller.incise(arg)


class ParamMeta(_Armature):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(KINDS['{kind}'])"
            )))


class Param(_IncisableHost, metaclass=ParamMeta):

    kind: str = 'PosKw'
    hint: type = GENERIC
    value: object = NotImplemented

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        kind, hint, value = bound.arguments.values()
        bound.arguments.update(
            kind=(KINDNAMES[kind.value] if isinstance(kind, _pkind) else kind),
            hint=(GENERIC if hint is _pempty else hint),
            value=(NotImplemented if value is _pempty else value),
            )
        return bound

    def get_parameter(self, name: str = 'anon', /):
        default = _pempty if (val:=self.value) is NotImplemented else val
        return _inspect.Parameter(
            name, KINDS[self.kind],
            default=default,
            annotation=self.hint,
            )

    def __call__(self, value, /):
        return self.__class_call__(self.kind, self.hint, value)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls(hint=arg)

    @property
    def retrieve(self, /):
        return self.degenerate

    def degenerate(self, index, /):
        return self.incise(super().degenerate(index))

    def incise(self, chora, /):
        return self.__class_call__(self.kind, chora, self.value)

    @property
    def chora(self, /):
        return self.hint

    def __getitem__(self, arg, /):
        if isinstance(arg, Param):
            return self.__class_call__(
                max(KINDS[param.kind] for param in (self, incisor)),
                self.hint[incisor.hint],
                (self.value if (val := incisor.value) is NotImplemented else val),
                )
        elif isinstance(arg, _Degenerate):
            return self.incise(arg)
        return super().__getitem__(arg)


class Sig(_IncisableHost, metaclass=_Armature):

    FIELDS = (_inspect.Parameter('params', 4),)

    @staticmethod
    def _get_orderscore(pair):
        _, obj = pair
        if isinstance(obj, _Degenerate):
            return -1
        adj = 0 if obj.value is NotImplemented else 0.5
        return KINDNAMES.index(obj.kind) + adj

    @classmethod
    def parameterise(cls, cache, arg=None, /, _chora=None, **params):
        if arg is None:
            params = dict(sorted(
                params.items(),
                key=cls._get_orderscore,
                ))
        elif not params:
            if isinstance(arg, _inspect.Signature):
                signature = arg
            else:
                signature = _inspect.signature(arg)
            cache['signature'] = signature
            params = {
                pm.name: Param(pm.annotation, pm.default, pm.kind)
                for pm in signature.parameters.values()
                }
        else:
            raise RuntimeError(
                f"Must provide exactly one of either arg or params "
                f"to {self.__class__._ptolemaic_class__}."
                )
        if _chora is not None:
            cache['chora'] = _chora
        return super().parameterise(cache, **params)

    @property
    @_caching.soft_cache()
    def signature(self, /):
        return _inspect.Signature(
            param.get_parameter(name) for name, param in self.params.items()
            if not isinstance(param.hint, _Degenerate)
            )

    @property
    def bind(self, /):
        return self.signature.bind

    @property
    @_caching.soft_cache()
    def chora(self, /):
        return _MultiMapp(**{key: val.hint for key, val in self.params.items()})

    def incise(self, chora, /):
        params = {
            key: Param(param.kind, cho, param.value)
            for ((key, param), cho) in zip(self.params.items(), chora.choras)
            }
        return self.__class_call__(_chora=chora, **params)

#     def incise(self, chora, /):
#         print('foo')
#         return self.__class_call__(**dict(zip(
#             chora,
#             (param[cho] for cho, param in zip(chora.choras, self.params.values()),
#             )))  # INEFFICIENT! MultiMapp gets created twice!

    def retrieve(self, index: tuple, /):
        return Params(self, index)

    @property
    @_caching.soft_cache()
    def __call__(self, /):
        return _functools.partial(Params, self)

    def __str__(self, /):
        return str(self.signature)


# DEFAULTSIG = Sig(args=Param.Args, kwargs=Param.Kwargs)

@_classtools.add_defer_meths('sigarguments', like=dict)
class Params(metaclass=_Armature):

    FIELDS = (
        _inspect.Parameter('signature', 0, annotation=Sig),
        _inspect.Parameter('content', 0, annotation=_mprox),
        )

    __slots__ = ('bound',)

    @classmethod
    def parameterise(cls, cache, arg0, arg1=None, /, **kwargs):
        if arg1 is None:
            if kwargs:
                return super().parameterise(cache, arg0, _mprox(kwargs))
            return super().parameterise(cache, arg0)
        if kwargs:
            raise ValueError("Cannot pass kwargs if two args are passed.")
        if not isinstance(arg1, _mprox):
            arg1 = _mprox(arg1)
        return super().parameterise(cache, arg0, arg1)

    def __init__(self, /):
        super().__init__()
        bound = self.bound = self.signature.signature.bind_partial()
        bound.apply_defaults()
        bound.arguments.update(self.content)

    @property
    def sigargs(self, /):
        return self.bound.args

    @property
    def sigkwargs(self, /):
        return _mprox(self.bound.kwargs)

    @property
    def sigarguments(self, /):
        return _mprox(self.bound.arguments)


class ParamProp:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        self.name = name

    def __get__(self, instance, _=None):
        return instance.params.sigarguments[self.name]


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

