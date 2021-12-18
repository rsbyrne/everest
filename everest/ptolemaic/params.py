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

from everest.ptolemaic.armature import (
    Armature as _Armature,
    ArmatureMeta as _ArmatureMeta,
    )
from everest.ptolemaic.chora import (
    ChoraAbstract as _ChoraAbstract,
    ChoraBase as _ChoraBase,
    Chora as _Chora,
    Degenerate as _Degenerate,
    ChoraMapp as _ChoraMapp,
    )

_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


KINDNAMES = ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs')
KINDS = dict(zip(KINDNAMES, _pkind))


class _GenericMeta_(type):

    def __repr__(cls, /):
        return cls.__name__


class Generic(metaclass=_GenericMeta_):

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls.getitem(cls, arg)

    @classmethod
    def getitem(cls, caller, arg, /):
        if isinstance(arg, _ChoraAbstract):
            return caller.incise(arg)
        raise TypeError(arg)

    @classmethod
    def incise(cls, arg, /):
        return arg


class ParamMeta(_ArmatureMeta):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(kind=KINDS['{kind}'])"
            )))


class ParamBase(_ChoraBase, _Armature, metaclass=ParamMeta):
    ...


class DegenerateParam(_Degenerate, ParamBase):

    @property
    def orderscore(self, /):
        return 0


class Param(ParamBase):

    hint: type = Generic
    value: object = NotImplemented
    kind: str = 'PosKw'

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = super().parameterise(*args, **kwargs)
        hint, value, kind = bound.arguments.values()
        bound.arguments.update(
            hint=(Generic if hint is _pempty else hint),
            value=(NotImplemented if value is _pempty else value),
            kind=(KINDNAMES[kind.value] if isinstance(kind, _pkind) else kind),
            )
        return bound

    def get_parameter(self, name: str = 'anon', /):
        default = _pempty if (val:=self.value) is NotImplemented else val
        return _inspect.Parameter(
            name, KINDS[self.kind],
            default=default,
            annotation=self.hint,
            )

    def __call__(self, /, **kwargs):
        return self.__class_call__(**dict(
            hint=self.hint, kind=self.kind, value=self.value
            ) | kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls()[arg]

    @property
    def orderscore(self, /):
        adj = 0 if self.value is NotImplemented else 0.5
        return KINDNAMES.index(self.kind) + adj

    def __getitem__(self, arg, /):
        if isinstance(arg, Param):
            return self.__class_call__(
                self.hint, arg.value, arg.kind
                )[arg.hint]
        return super().__getitem__(arg)

    def getitem(self, caller, arg, /):
        return self.hint.getitem(caller, arg)

    def incise(self, chora, /):
        return self.__class_call__(chora, self.value, self.kind)

    @property
    def degenerate(self, /):
        return DegenerateParam


# @_classtools.add_defer_meths('params', like=dict)
class Sig(_ChoraMapp):

    __slots__ = ('signature',)

    @classmethod
    def parameterise(cls, arg=None, /, **params):
        if arg is None:
            params = dict(sorted(
                params.items(),
                key=lambda x: x[1].orderscore,
                ))
        elif not params:
            if isinstance(arg, _inspect.Signature):
                signature = arg
            else:
                signature = _inspect.signature(arg)
            params = {
                pm.name: Param(pm.annotation, pm.default, pm.kind)
                for pm in signature.parameters.values()
                }
        else:
            raise RuntimeError(
                f"Must provide exactly one of either arg or params "
                f"to {self.__class__._ptolemaic_class__}."
                )
        return super().parameterise(**params)

    @property
    def params(self, /):
        return self.chorakws

    def __init__(self, /):
        super().__init__()
        self.signature = _inspect.Signature(
            param.get_parameter(name) for name, param in self.params.items()
            if not isinstance(param, _Degenerate)
            )

    @property
    def bind(self, /):
        return self.signature.bind

    @property
    @_caching.soft_cache()
    def __call__(self, /):
        return _functools.partial(Params, self)

    @property
    @_caching.soft_cache()
    def commence(self, /):
        return _functools.partial(Params.instantiate, self)

    def __str__(self, /):
        return str(self.signature)


# DEFAULTSIG = Sig(args=Param.Args, kwargs=Param.Kwargs)


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


# class ParamProp:

#     __slots__ = ('name',)

#     def __init__(self, name: str, /):
#         self.name = name

#     def __get__(self, instance, _=None):
#         return instance.params.arguments[self.name]


###############################################################################
###############################################################################
