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

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


KINDNAMES = ('Pos', 'PosKw', 'Args', 'Kw', 'Kwargs')
KINDS = dict(zip(KINDNAMES, _inspect._ParameterKind))


class _GenericMeta_(type):

    def __repr__(cls, /):
        return cls.__name__


class Generic(metaclass=_GenericMeta_):

    def __class_getitem__(cls, arg, /):
        if isinstance(arg, type):
            return arg
        raise KeyError(arg)


class ParamMeta(_Essence):

    for kind in KINDS:
        exec('\n'.join((
            '@property',
            f'def {kind}(cls, /):'
            f"    return cls(kind='{kind}')"
            )))


class Param(_Ptolemaic, metaclass=ParamMeta):

    __slots__ = ('hint', 'value', 'kind')

    @classmethod
    def _check_hint(cls, hint, /):
        if hint is _inspect._empty:
            return Generic
        return hint

    def __init__(self, /,
            hint=Generic,
            value=NotImplemented,
            kind='PosKw',
            ):
        super().__init__()
        if kind not in KINDNAMES:
            kind = KINDNAMES[kind.value]
        hint = self._check_hint(hint)
        self.kind, self.hint = kind, hint
        if kind in {'Args', 'Kwargs'}:
            if value is not NotImplemented:
                raise TypeError
        self.value = NotImplemented if value is _inspect._empty else value

    @property
    def truekind(self, /):
        return KINDS[self.kind]

    @property
    def truehint(self, /):
        return (
            _inspect._empty
            if (hint := self.hint) is Generic
            else hint
            )

    @property
    def truevalue(self, /):
        return (
            _inspect._empty
            if (value := self.value) is NotImplemented
            else value
            )

    def get_parameter(self, name: str = 'anon', /):
        return _inspect.Parameter(
            name, self.truekind,
            default=self.truevalue,
            annotation=self.truehint,
            )

    def __call__(self, **kwargs):
        return self.__class__(**dict(
            hint=self.hint, kind=self.kind, value=self.value
            ) | kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls()[arg]

    def __getitem__(self, arg, /):
        if isinstance(arg, Param):
            return self(**{**arg.inps, 'hint': self.hint[arg.hint]})
        return self(hint=self.hint[arg])



    @property
    def orderscore(self, /):
        adj = 0 if self.value is NotImplemented else 0.5
        return self.truekind.value + adj

    def get_epitaph(self, /):
        return self.taphonomy.callsig_epitaph(
            self.__class__._ptolemaic_class__,
            self.hint, self.value, self.kind,
            )

    def _repr(self, /):
        return _format_argskwargs(self.hint, self.value, self.kind)

    def __str__(self, /):
        return f"{self.kind}:{self.hint}={self.value}"


# @_classtools.add_defer_meths('params', like=dict)
class Sig(_Ptolemaic):

    __slots__ = ('params', 'signature')

    def __init__(self, arg=None, /, **params):
        super().__init__()
        if arg is None:
            params = dict(sorted(
                params.items(),
                key=lambda x: x[1].orderscore,
                ))
            signature = _inspect.Signature(
                param.get_parameter(name) for name, param in params.items()
                )
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
        self.params = _types.MappingProxyType(params)
        self.signature = signature

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

    def get_epitaph(self, /):
        return self.taphonomy.callsig_epitaph(
            self.__class__._ptolemaic_class__, **self.params
            )

    def _repr(self, /):
        return _format_argskwargs(**self.params)

    def __str__(self, /):
        return str(self.signature)


DEFAULTSIG = Sig(args=Param.Args, kwargs=Param.Kwargs)


class Params(_Ptolemaic):

    __slots__ = (
        'signature', '_args', '_kwargs', 'args', 'kwargs',
        'arguments', '_getmeths', '_setmeths',
        )

    def __init__(self, signature=DEFAULTSIG, /, *args, **kwargs):
        super().__init__()
        self.signature = signature
        args = self._args = list(args)
        self._kwargs = kwargs
        self.kwargs = _types.MappingProxyType(kwargs)
        self._getmeths = {int: args.__getitem__, str: kwargs.__getitem__}
        self._setmeths = {int: args.__setitem__, str: kwargs.__setitem__}

    def __finish__(self, /):
        args, kwargs = self._args, self._kwargs
        bound = self.signature.bind(*args, **kwargs)
        bound.apply_defaults()
        args[:] = bound.args
        kwargs.update(bound.kwargs)
        self.args = tuple(args)
        self.arguments = _types.MappingProxyType(bound.arguments)
        super().__finish__()

    def __getitem__(self, arg, /):
        if self.finalised:
            return self.arguments[arg]
        return self._getmeths[type(arg)](arg)

    def __setitem__(self, arg, val, /):
        if self.finalised:
            raise RuntimeError("This object has been finalised.")
        return self._setmeths[type(arg)](arg, val)

    def __call__(self, /, *args, **kwargs):
        if self.finalised:
            raise RuntimeError("This object has been finalised.")
        self._args.extend(args)
        self._kwargs.update(kwargs)

    def get_epitaph(self, /):
        return self.taphonomy.callsig_epitaph(
            self.__class__._ptolemaic_class__,
            self.signature, *self._args, **self._kwargs,
            )

    def __str__(self, /):
        return _format_argskwargs(*self.args, **self.kwargs)

    def _repr(self, /):
        return f"{repr(self.signature)}, {str(self)}"


class ParamProp:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        self.name = name

    def __get__(self, instance, _=None):
        return instance.params.arguments[self.name]


###############################################################################
###############################################################################
