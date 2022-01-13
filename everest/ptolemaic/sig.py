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
    FrozenMap as _FrozenMap,
    reseed as _reseed,
    )
from everest import epitaph as _epitaph
from everest.incision import (
    Incisable as _Incisable,
    ChainIncisable as _ChainIncisable,
    )

from everest.ptolemaic.armature import (
    Armature as _Armature,
    MultiMap as _MultiMap,
    Degenerate as _Degenerate,
    )
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.thing import Thing as _Thing
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence

_pkind = _inspect._ParameterKind
_pempty = _inspect._empty

_mprox = _types.MappingProxyType


class ParamKind(_Enum):

    POS = _pkind['POSITIONAL_ONLY']
    POSKW = _pkind['POSITIONAL_OR_KEYWORD']
    ARGS = _pkind['VAR_POSITIONAL']
    KW = _pkind['KEYWORD_ONLY']
    KWARGS = _pkind['VAR_KEYWORD']

    __slots__ = ('_epitaph',)

    def __repr__(self, /):
        return f"<ParamKind[{self.name}]>"

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

    def __gt__(self, other, /):
        return self.score > other.score

    def __lt__(self, other, /):
        return self.score < other.score

    def __ge__(self, other, /):
        return self.score >= other.score

    def __le__(self, other, /):
        return self.score <= other.score

    def __eq__(self, other, /):
        return self.score == other.score

    def __ne__(self, other, /):
        return self.score != other.score

    def __hash__(self, /):
        return self.epitaph.hashint


class FieldMeta(_Sprite):

    for kind in ParamKind:
        exec('\n'.join((
            '@property',
            f'def {kind.name}(cls, /):'
            f"    return FieldKind(ParamKind.{kind.name})"
            )))


class FieldKind(metaclass=FieldMeta):

    kind: ParamKind

    def __call__(self, /, *args, **kwargs):
        return Field(self.kind, *args, **kwargs)

    def __getitem__(self, arg, /):
        if isinstance(arg, FieldKind):
            kind = max(arg.kind, self.kind)
            return FieldKind(kind)
        return Field(self.kind, arg)


class Field(_ChainIncisable, metaclass=FieldMeta):

    kind: ParamKind
    hint: _Incisable
    value: object

    @property
    def chora(self, /):
        return self.hint

    @classmethod
    def __new__(cls, /,
            kind=ParamKind.POSKW, hint=_Thing, value=NotImplemented
            ):
        if isinstance(kind, _pkind):
            kind = ParamKind.convert(kind)
        elif not isinstance(kind, ParamKind):
            raise TypeError(f"Kind must be `ParamKind`.")
        if isinstance(hint, _Degenerate):
            value = NotImplemented
        else:
            if hint is _pempty:
                hint = _Thing
            elif not isinstance(hint, _Incisable):
                raise TypeError(
                    f"The `Field` hint must be an instance of `Incisable`:\n"
                    f"{hint}"
                    )
            if value is _pempty:
                value = NotImplemented
            elif value is not NotImplemented:
                if value not in hint:
                    raise ValueError(
                        f"The default value must be a member "
                        f"of the provided 'hint' `Incisable`: "
                        f"`{value} in {hint}` must be `True`."
                        )
        return super().__new__(cls, kind, hint, value)

    def get_parameter(self, name: str = 'anon', /):
        default = _pempty if (val:=self.value) is NotImplemented else val
        return _inspect.Parameter(
            name, self.kind.value,
            default=default,
            annotation=self.hint,
            )

    def __call__(self, arg, /):
        return self._ptolemaic_class__(
            kind=self.kind, hint=self.hint, value=arg
            )

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls(hint=arg)

    def __incise_retrieve__(self, incisor, /):
        return self.__incise_slyce__(_Degenerate(incisor))

    def __incise_slyce__(self, incisor, /):
        return self._ptolemaic_class__(self.kind, incisor, self.value)

    def __getitem__(self, arg, /):
        if isinstance(arg, Field):
            incval = arg.value
            return self._ptolemaic_class__(
                max(param.kind for param in (self, arg)),
                arg.hint,
                (self.value if incval is NotImplemented else incval),
                )
        if isinstance(arg, FieldKind):
            return self._ptolemaic_class__(
                max(param.kind for param in (self, arg)),
                self.hint,
                self.value,
                )
        if isinstance(arg, _Degenerate):
            return self.__incise_slyce__(arg)
        return super().__getitem__(arg)

    @property
    def __contains__(self, /):
        return self.hint.__contains__


class Sig(_ChainIncisable, _Armature, metaclass=_Sprite):

    infields: _FrozenMap = _FrozenMap()

    @property
    @_caching.soft_cache()
    def chora(self, /):
        return _MultiMap(**{
            key: val.hint for key, val in self.infields.items()
            })

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
    def __new__(cls, arg0=None, arg1=None, /, **kwargs):
        cache = {}
        if arg1 is None:
            if arg0 is None:
                fields = {
                    key: field() if isinstance(field, FieldKind) else field
                    for key, field in kwargs.items()
                    }
            else:
                if kwargs:
                    raise TypeError
                if isinstance(arg0, _inspect.Signature):
                    signature = arg0
                else:
                    signature = _inspect.signature(arg0)
                cache['signature'] = signature
                fields = {
                    pm.name: Field(pm.kind, pm.annotation, pm.default)
                    for pm in signature.parameters.values()
                    }
        else:
            if kwargs:
                raise TypeError
            cache['chora'], fields = arg0, arg1
        obj = super().__new__(cls, _FrozenMap(cls._sort_fields(fields)))
        if cache:
            obj.softcache.update(cache)
        return obj

    @property
    @_caching.soft_cache()
    def degenerates(self, /):
        return _mprox({
            name: field.hint.value
            for name, field in self.infields.items()
            if isinstance(field.hint, _Degenerate)
            })

    @property
    @_caching.soft_cache()
    def signature(self, /):
        return _inspect.Signature(
            field.get_parameter(name)
            for name, field in self.infields.items()
            )

    @property
    @_caching.soft_cache()
    def effsignature(self, /):
        return _inspect.Signature(
            parameter for name, parameter in self.signature.parameters.items()
            if name not in self.degenerates
            )

    def __incise_slyce__(self, chora, /):
        assert isinstance(chora, _MultiMap)
        fields = {
            key: Field(field.kind, cho, field.value)
            for ((key, field), cho) in zip(self.infields.items(), chora.choras)
            }
        return self._ptolemaic_class__(chora, fields)

    def __incise_retrieve__(self, index: dict, /):
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
        fields = self.infields
        for key, val in bound.arguments.items():
            if val not in fields[key]:
                raise ValueError(key, val, type(val))
        return Params(bound)

    def __str__(self, /):
        return str(self.effsignature)

    def _repr_pretty_(self, p, cycle):
        p.text('<')
        root = repr(self._ptolemaic_class__)
        if cycle:
            p.text(root + '{...}')
        elif not (kwargs := self.infields):
            p.text(root + '()')
        else:
            with p.group(4, root + '(', ')'):
                kwargit = iter(kwargs.items())
                p.breakable()
                key, val = next(kwargit)
                p.text(key)
                p.text(' = ')
                p.pretty(val)
                for key, val in kwargit:
                    p.text(',')
                    p.breakable()
                    p.text(key)
                    p.text(' = ')
                    p.pretty(val)
                p.breakable()
        p.text('>')


@_classtools.add_defer_meths('arguments', like=dict)
class Params(metaclass=_Sprite):

    nargs: int = 0
    arguments: _FrozenMap = _FrozenMap()

    def __new__(cls, arg0=0, arg1=None, /, **kwargs):
        cache = {}
        if arg1 is None:
            if isinstance(arg0, _inspect.BoundArguments):
                if kwargs:
                    raise TypeError
                cache['sigkwargs'] = arg0.kwargs
                bndargs = cache['sigargs'] = arg0.args
                nargs = len(bndargs)
                arguments = arg0.arguments
            else:
                nargs = arg0
                arguments = kwargs
        else:
            if kwargs:
                raise TypeError
            nargs, arguments = arg0, arg1
        obj = super().__new__(cls, int(nargs), _FrozenMap(arguments))
        if cache:
            obj.softcache.update(cache)
        return obj

    @property
    @_caching.soft_cache()
    def sigargs(self, /):
        return tuple(self.arguments.values())[:self.nargs]

    @property
    @_caching.soft_cache()
    def sigkwargs(self, /):
        dct = self.arguments
        return {name: dct[name] for name in tuple(dct)[self.nargs:]}


class Param(metaclass=_Sprite):

    name: str

    def __get__(self, instance, _=None):
        try:
            return instance.params[self.name]
        except KeyError:
            raise AttributeError(self.name)
        except AttributeError:
            return self


###############################################################################
###############################################################################

