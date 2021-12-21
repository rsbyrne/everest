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
    )
from everest.ptolemaic import chora as _chora
from everest.ptolemaic.chora import (
    ChoraBase as _ChoraBase,
    PseudoChora as _PseudoChora,
    Degenerate as _Degenerate,
    MultiMapp as _MultiMapp,
    )

_pkind = _inspect._ParameterKind
_pempty = _inspect._empty

_mprox = _types.MappingProxyType


KINDNAMES = ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs')
KINDS = dict(zip(KINDNAMES, _pkind))


class ParamMeta(_Armature):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(KINDS['{kind}'])"
            )))


class ParamBase(_ChoraBase, metaclass=ParamMeta):
    ...


class DegenerateParam(_Degenerate, ParamBase):

    @property
    def orderscore(self, /):
        return 0


class Generic(_PseudoChora):

    def incise_chora(self, incisor: _ChoraBase, /):
        return incisor

    def incise_type(self, incisor: type, /):
        return incisor

    def __repr__(self, /):
        return 'GENERIC'


GENERIC = Generic()


class Param(_PseudoChora, ParamBase):

    kind: str = 'PosKw'
    hint: type = GENERIC
    value: object = NotImplemented

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = super().parameterise(*args, **kwargs)
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
    def degenerate(self, /):
        return DegenerateParam

    def incise_param(self, incisor: ParamBase, /):
        return self.__class_call__(
            max(KINDS[param.kind] for param in (self, incisor)),
            self.hint[incisor.hint],
            (self.value if (val := incisor.value) is NotImplemented else val),
            )

    def fallback_object(self, caller, incisor: object, /):
        return self.hint.getitem(caller, incisor)

    def incise(self, chora, /):
        return self.__class_call__(self.kind, chora, self.value)

    def retrieve(self, index, /):
        return self.degenerate(index)

    @property
    def orderscore(self, /):
        adj = 0 if self.value is NotImplemented else 0.5
        return KINDNAMES.index(self.kind) + adj


class Sig(_MultiMapp):

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

    def retrieve(self, index: tuple, /):
        return Params(self, index)

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

@_classtools.add_defer_meths('sigarguments', like=dict)
class Params(metaclass=_Armature):

    FIELDS = (
        _inspect.Parameter('signature', 0, annotation=Sig),
        _inspect.Parameter('content', 0, annotation=_mprox),
        )

    __slots__ = ('bound',)

    @classmethod
    def parameterise(cls, arg0, arg1=None, /, **kwargs):
        if arg1 is None:
            if kwargs:
                return super().parameterise(arg0, _mprox(kwargs))
            return super().parameterise(arg0)
        if kwargs:
            raise ValueError("Cannot pass kwargs if two args are passed.")
        if not isinstance(arg1, _mprox):
            arg1 = _mprox(arg1)
        return super().parameterise(arg0, arg1)

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

