###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import functools as _functools
import types as _types
import collections.abc as _collabc
from collections import deque as _deque
import operator as _operator
from enum import Enum as _Enum

from everest.utilities import (
    caching as _caching,
    classtools as _classtools,
    format_argskwargs as _format_argskwargs,
    reseed as _reseed,
    pretty as _pretty,
    Slc as _Slc,
    )
from everest import epitaph as _epitaph
from everest.incision import (
    IncisionProtocol as _IncisionProtocol,
    Incisable as _Incisable,
    )

from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.diict import Kwargs as _Kwargs
from everest.ptolemaic.bythos import Bythos as _Bythos
from everest.ptolemaic.essence import Essence as _Essence

from .thing import Thing as _Thing
from .brace import Brace as _Brace
from .chora import (
    Chora as _Chora,
    ChainChora as _ChainChora,
    Multi as _Multi,
    Degenerate as _Degenerate,
    )


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


class FieldBase(metaclass=_Essence):

    @_abc.abstractmethod
    def get_parameter(self, name: str = 'anon', /) -> _pkind:
        raise NotImplementedError


class FieldKind(FieldBase, metaclass=_Sprite):

    kind: ParamKind

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        

    def __call__(self, /, *args, **kwargs):
        return Field(self.kind, *args, **kwargs)

    def __getitem__(self, arg, /):
        if isinstance(arg, FieldKind):
            kind = max(arg.kind, self.kind)
            return FieldKind(kind)
        return Field(self.kind, arg)

    @property
    def get_parameter(self, /):
        return self().get_parameter


with FieldBase.mutable:
    for kind in ParamKind:
        setattr(FieldBase, name := kind.name, FieldKind(ParamKind[name]))


class Field(_ChainChora, FieldBase, metaclass=_Sprite):

    kind: ParamKind
    hint: _Chora
    value: object

    @classmethod
    def __class_call__(cls, /,
            kind=ParamKind.POSKW, hint=_Thing, value=NotImplemented
            ):
        kind = cls.process_kind(kind)
        hint = cls.process_hint(hint)
        value = cls.process_value(value, hint)
        return super().__class_call__(kind, hint, value)

    @classmethod
    def process_kind(cls, kind, /):
        if isinstance(kind, _pkind):
            return ParamKind.convert(kind)
        if not isinstance(kind, ParamKind):
            raise TypeError(f"Kind must be `ParamKind`.")
        return kind

    @classmethod
    def process_hint(cls, hint, /):
        if hint in (_pempty, object):
            return _Thing
        if not isinstance(hint, _Chora):
            raise TypeError(
                f"The `Field` hint must be an instance of `Chora`:\n"
                f"{hint}"
                )
        return hint

    @classmethod
    def process_value(cls, value, hint, /):
        if value is _pempty:
            return NotImplemented
        return value

    def get_parameter(self, name: str = 'anon', /):
        default = _pempty if (val:=self.value) is NotImplemented else val
        return _inspect.Parameter(
            name, self.kind.value,
            default=default,
            annotation=self.hint,
            )

    @property
    def __incision_manager__(self, /):
        return self.hint

    def __call__(self, arg, /):
        return self._ptolemaic_class__(
            kind=self.kind, hint=self.hint, value=arg
            )

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls(hint=arg)

    def degenerate(self, /):
        return DegenerateField(self.kind, self.hint, self.value)

    def __incise_degenerate__(self, incisor, /):
        assert isinstance(incisor, Field)
        return incisor.degenerate()

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


    class Degenerate(FieldBase, metaclass=_Essence):

        @property
        def kind(self, /):
            return self.value.kind

# class DegenerateField(_Degenerate, _FullField_, metaclass=_Sprite):

#     hint: _Incisable
#     value: object


class Params(metaclass=_Sprite):

    nargs: int = 0
    arguments: _Kwargs = _Kwargs()

    _req_slots__ = ('__dict__',)

    for name in (
            '__getitem__', '__len__', '__iter__', '__contains__',
            'keys', 'values', 'items',
            ):
        exec('\n'.join((
            f'@property',
            f'def {name}(self, /):',
            f'    return self.arguments.{name}',
            )))
    del name

    def __init__(self, /):
        self.__dict__.update(self.arguments)

    @classmethod
    def __class_call__(cls, arg0=0, arg1=None, /, **kwargs):
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
        obj = super().__class_call__(int(nargs), _Kwargs(arguments))
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


def gather_fields(bases: iter, fields: dict, /) -> dict:
    try:
        base = next(bases)
    except StopIteration:
        return
    anno = base.__dict__.get('__annotations__', {})
    gather_fields(bases, fields)
    for name, note in anno.items():
        default = base.__dict__.get(name, NotImplemented)
        deq = fields.setdefault(name, _deque())
        if note is Field:
            field = note()
        elif isinstance(note, (Field, FieldKind)):
            field = note
        else:
            field = Field[note]
        if name in base.__dict__:
            field = field(base.__dict__[name])
        deq.append(field)


def get_typ_fields(typ):
    gather_fields(iter(typ.__mro__), fields := {})
    for name, deq in tuple(fields.items()):
        if len(deq) == 1:
            field = deq[0]
        else:
            field = _functools.reduce(_operator.getitem, reversed(deq))
        if isinstance(field, FieldKind):
            field = field[_Thing]
        fields[name] = field
    return fields


class Sig(_ChainChora, metaclass=_Sprite):

    sigfields: _Kwargs

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
    def __class_call__(cls, arg=None, /, **kwargs):
        cache = {}
        if arg is None:
            fields = {
                key: field() if isinstance(field, FieldKind) else field
                for key, field in kwargs.items()
                }
        else:
            if kwargs:
                raise TypeError
            if isinstance(arg, _Kwargs):
                fields = arg
            elif isinstance(arg, type):
                fields = get_typ_fields(arg)
            else:
                if isinstance(arg, _inspect.Signature):
                    signature = arg
                else:
                    signature = _inspect.signature(arg)
                cache['signature'] = signature
                fields = {
                    pm.name: Field(pm.kind, pm.annotation, pm.default)
                    for pm in signature.parameters.values()
                    }
        if not all(isinstance(field, FieldBase) for field in fields.values()):
            raise TypeError(fields)
        obj = super().__class_call__(_Kwargs(cls._sort_fields(fields)))
        if cache:
            obj.softcache.update(cache)
        return obj

    @property
    @_caching.soft_cache()
    def __incision_manager__(self, /):
        return _Brace[_Kwargs(**{
            key: field.hint
            for key, field in self.sigfields.items()
            })]

    @property
    @_caching.soft_cache()
    def degenerates(self, /):
        return _mprox({
            name: field.hint.retrieve()
            for name, field in self.sigfields.items()
            if isinstance(field.hint, _Degenerate)
            })

    @property
    @_caching.soft_cache()
    def signature(self, /):
        return _inspect.Signature(
            field.get_parameter(name)
            for name, field in self.sigfields.items()
            )

    @property
    @_caching.soft_cache()
    def effsignature(self, /):
        return _inspect.Signature(
            parameter for name, parameter in self.signature.parameters.items()
            if name not in self.degenerates
            )

    def __incise_retrieve__(self, incisor: _Brace, /):
        bound = self.signature.bind_partial()
        bound.arguments.update(zip(self.sigfields, incisor))
        bound.arguments.update(self.degenerates)
        bound.apply_defaults()
        return Params(bound)

    def __incise_slyce__(self, incisor: _Brace.Oid, /):
        obj = self._ptolemaic_class__(**{
            key: Field(field.kind, chora, field.value)
            for (key, field), chora
            in zip(self.sigfields.items(), incisor.choras)
            })
        obj.softcache.update(
            __incision_manager__=incisor,
            signature=self.signature
            )
        return obj

    def __call__(self, /, *args, **kwargs):
        return Params(self.effsignature.bind(*args, **kwargs))

    def __contains__(self, params: Params) -> bool:
        fields = self.sigfields
        for key, val in params.items():
            if not val in fields[key]:
                return False
        return True

    for name in ('keys', 'values', 'items'):
        exec('\n'.join((
            f'@property',
            f'def {name}(self, /):',
            f'    return self.content.{name}',
            )))
    del name

    def __str__(self, /):
        return str(self.effsignature)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        self.__incision_manager__._repr_pretty_(p, cycle, root)


class Param:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        super().__init__()
        self.name = name

    def __get__(self, instance, _=None):
        try:
            return instance.params[self.name]
        except KeyError:
            raise AttributeError(self.name)
        # except AttributeError:
        #     return self


###############################################################################
###############################################################################

