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


class FieldMeta(_Armature):

    for kind in ParamKind:
        exec('\n'.join((
            '@property',
            f'def {kind.name}(cls, /):'
            f"    return cls(ParamKind.{kind.name})"
            )))


class Field(_Incisable, metaclass=FieldMeta):

    kind: str = ParamKind.Pos
    hint: type = GENERIC
    value: object = NotImplemented

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        kind, hint, value = bound.arguments.values()
        if isinstance(kind, _pkind):
            kind = ParamKind.convert(kind)
        if isinstance(hint, _Degenerate):
            pass
#             value = hint.value
        else:
            if hint is _pempty:
                hint = GENERIC
            if value is _pempty:
                value = NotImplemented
        bound.arguments.update(kind=kind, hint=hint, value=value)
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
        if isinstance(arg, Field):
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
        _inspect.Parameter('chora', 0, default=None),
        _inspect.Parameter('fields', 4),
        )

    @staticmethod
    def _get_orderscore(pair):
        _, obj = pair
        if isinstance(obj, _Degenerate):
            return -1
        adj = 0 if obj.value is NotImplemented else 0.5
        return obj.kind.score + adj

    @staticmethod
    def _sort_fields(dct):
        return dict(sorted(dct.items(), key=Sig._get_orderscore))

    @classmethod
    def parameterise(cls, cache,
            arg=None, /, *,
            _signature_=None, **kwargs,
            ):
        if isinstance(arg, _Chora):
            if _signature_ is not None:
                cache['signature'] = _signature_
            kwargs = cls._sort_fields(kwargs)
        else:
            if arg is not None:
                if _signature_ is not None:
                    raise RuntimeError(
                        "Cannot provide signature as both arg and kwarg."
                        )
                if kwargs:
                    raise RuntimeError(
                        "Cannot provide fields when args are provided."
                        )
                if isinstance(arg, _inspect.Signature):
                    _signature_ = arg
                else:
                    _signature_ = _inspect.signature(arg)
                kwargs = cls._sort_fields({
                    pm.name: Field(pm.kind, pm.annotation, pm.default)
                    for pm in _signature_.parameters.values()
                    })
                cache['signature'] = _signature_
            arg = _MultiMapp(**{
                key: val.hint for key, val in kwargs.items()
                })
        return super().parameterise(cache, arg, **kwargs)

    @property
    @_caching.soft_cache()
    def degenerates(self, /):
        return _mprox({
            name: field.hint.value
            for name, field in self.fields.items()
            if isinstance(field.hint, _Degenerate)
            })

    @property
    @_caching.soft_cache()
    def signature(self, /):
        return _inspect.Signature(
            field.get_parameter(name)
            for name, field in self.fields.items()
            )

    @property
    @_caching.soft_cache()
    def effsignature(self, /):
        return _inspect.Signature(
            parameter for name, parameter in self.signature.parameters.items()
            if name not in self.degenerates
            )

    def incise(self, chora, /):
        assert isinstance(chora, _MultiMapp)
        fields = {
            key: Field(field.kind, cho, field.value)
            for ((key, field), cho) in zip(self.fields.items(), chora.choras)
            }
        return self.__class_call__(chora, **fields)

    def retrieve(self, index: dict, /):
        bound = self.signature.bind_partial()
        bound.arguments.update(index)
        bound.apply_defaults()
        return Params(bound)

    def __call__(self, /, *args, **kwargs):
        effbound = self.effsignature.bind(*args, **kwargs)
        bound = self.signature.bind_partial()
        bound.arguments.update(effbound.arguments)
        bound.arguments.update(self.degenerates)
        bound.apply_defaults()
        return Params(bound)

    def __str__(self, /):
        return str(self.effsignature)


@_classtools.add_defer_meths('_arguments', like=dict)
class Params(metaclass=_Armature):

    FIELDS = (
        _inspect.Parameter('nargs', 0, default=0),
        _inspect.Parameter('_arguments', 4),
        )

    @classmethod
    def parameterise(cls, cache, arg0=None, /, **kwargs):
        if isinstance(arg0, _inspect.BoundArguments):
            bndargs = cache['sigargs'] = arg0.args
            cache['sigkwargs'] = arg0.kwargs
            return super().parameterise(cache, len(bndargs), **arg0.arguments)
        elif arg0 is None:
            return super().parameterise(cache, **kwargs)
        return super().parameterise(cache, arg0, **kwargs)

    @property
    @_caching.soft_cache()
    def sigargs(self, /):
        return tuple(self._arguments.values())[:self.nargs]

    @property
    @_caching.soft_cache()
    def sigkwargs(self, /):
        dct = self._arguments
        return {name: dct[name] for name in tuple(dct)[self.nargs:]}


class ParamProp:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        self.name = name

    def __get__(self, instance, _=None):
        return instance.params[self.name]


###############################################################################
###############################################################################

