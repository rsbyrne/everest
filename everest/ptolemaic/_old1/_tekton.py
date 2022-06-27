###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import functools as _functools
from types import SimpleNamespace as _SimpleNamespace
from collections import abc as _collabc, namedtuple as _namedtuple

from everest import ur as _ur

from .urgon import Urgon as _Urgon
from .content import Kwargs as _Kwargs
from . import smartattr as _smartattr


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


class Fields(_Kwargs):

    __slots__ = ('signature', 'defaults', 'degenerates')

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return super().parameterise(cls.__content_type__(
            sorted(dict(*args, **kwargs).items(), key=(lambda x: x[1].score))
            ))

    def __init__(self, /):
        super().__init__()
        degenerates = self.degenerates = _ur.DatDict({
            name: field.default
            for name, field in self.items() if field.degenerate
            })
        signature = self.signature = _inspect.Signature(
            field.get_parameter(name)
            for name, field in self.items() if name not in degenerates
            )
        self.defaults = _ur.DatDict({
            param.name: param.default
            for param in signature.parameters.values()
            if param.default is not param.empty
            })

    def __call__(self, /, *args, **kwargs):
        return tuple({
            **self.signature.bind(*args, **kwargs).arguments,
            **self.degenerates
            }.values())

    def __contains__(self, fieldvals: tuple) -> bool:
        for val, field in zip(fieldvals, self):
            if val not in field:
                return False
        return True

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        return instance.params


class Field(_smartattr.SmartAttr):

    __slots__ = ('score',)

    default: object
    kind: object

    __merge_fintyp__ = Fields

    KINDPAIRS = _ur.DatDict(
        POS = _pkind['POSITIONAL_ONLY'],
        POSKW = _pkind['POSITIONAL_OR_KEYWORD'],
        ARGS = _pkind['VAR_POSITIONAL'],
        KW = _pkind['KEYWORD_ONLY'],
        KWARGS = _pkind['VAR_KEYWORD'],
        )

    @staticmethod
    def process_default(arg, /):
        if arg is _pempty:
            return NotImplemented
        return arg

    @classmethod
    def process_kind(cls, arg, /):
        if arg in (_pempty, NotImplemented):
            return 'POSKW'
        if arg not in cls.KINDPAIRS:
            raise ValueError(arg)
        return arg

    def __init__(self, /):
        super().__init__()
        kind = self.kind
        default = self.default
        if self.degenerate:
            self.score = -1
        else:
            self.score = sum((
                tuple(self.KINDPAIRS).index(kind),
                (0 if default is NotImplemented else 0.5),
                ))

    def get_parameter(self, name, /):
        return _inspect.Parameter(
            name, self.KINDPAIRS[self.kind],
            default=_pempty if (val:=self.default) is NotImplemented else val,
            annotation=self.hint,
            )

    # def __class_getitem__(cls, arg, /):
    #     return FieldHint('POSKW', arg)

    @classmethod
    def from_annotation(cls, anno, value):
        if isinstance(anno, FieldAnno):
            hint, note, kind = anno
            return cls(hint, note, value, kind)
        if anno is cls:
            return cls(default=value)
        return cls(anno, default=value)

    def __bound_get__(self, instance, name, /):
        return getattr(instance.params, name)

    def __bound_owner_get__(self, owner, name, /):
        return self.hint


class FieldAnno:

    def __iter__(self, /):
        return
        yield

    def __repr__(self, /):
        return f"{type(self).__qualname__}({', '.join(map(repr, self))})"


class FieldKind(FieldAnno):

    def __init__(self, /, kind=_pempty):
        self.kind = kind

    def __iter__(self, /):
        yield from (NotImplemented, NotImplemented, self.kind)

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, note=note)

    def __getitem__(self, hint, /):
        return FieldHint(kind=self.kind, hint=hint)


with Field.mutable:
    for kindname in Field.KINDPAIRS:
        setattr(Field, kindname, FieldKind(kindname))
del kindname


class FieldHint(FieldAnno):

    def __init__(self, /, kind=_pempty, hint=_pempty):
        self.kind, self.hint = kind, hint

    def __iter__(self, /):
        yield from (self.hint, NotImplemented, self.kind)

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, hint=self.hint, note=note)


class FieldNote(FieldAnno):

    def __init__(self, kind=_pempty, hint=_pempty, note=_pempty):
        self.kind, self.hint, self.note = kind, hint, note

    def __iter__(self, /):
        yield from (self.hint, self.note, self.kind)


class Tekton(_Urgon):

    @classmethod
    def field(meta, body, arg: Field = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.field, body, **kwargs)
        altname = f'_sm_{arg.__name__}'
        body.safe_set(altname, arg)
        return meta.Field(hint=altname, **kwargs)

    @classmethod
    def _yield_bodymeths(meta, /):
        yield from super()._yield_bodymeths()
        yield 'get', \
            lambda _, *ar, **kw: _smartattr.InstanceGet(*ar, **kw)
        yield 'oget', \
            lambda _, *ar, **kw: _smartattr.OwnerGet(*ar, **kw)
        for smartattrtype in meta._smartattrtypes:
            nm = smartattrtype.__name__.lower()
            yield nm, getattr(meta, nm)

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield Field

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        for typ in meta._smartattrtypes:
            yield \
                typ.__merge_name__, typ.__merge_dyntyp__, typ.__merge_fintyp__

    @classmethod
    def __meta_init__(meta, /):
        typs = meta._smartattrtypes = tuple(meta._yield_smartattrtypes())
        for typ in typs:
            setattr(meta, typ.__name__, typ)
        super().__meta_init__()

    @classmethod
    def _process_bodyanno(meta, body, name, hint, val, /):
        return name, meta.Field.from_annotation(hint, val)


class _TektonBase_(metaclass=Tekton):

    @classmethod
    def _get_signature(cls, /):
        return cls.__fields__.signature

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        Params = cls.Params = _namedtuple(
            f"Params_{cls.__name__}", cls.__fields__
            )
        cls.arity = len(Params._fields)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return super().parameterise(**bound.arguments)


###############################################################################
###############################################################################