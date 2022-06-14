###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools

from everest import ur as _ur

from .smartattr import SmartAttr as _SmartAttr
from .content import Kwargs as _Kwargs


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


class Field(_SmartAttr):

    __slots__ = ('score',)

    default: object
    kind: object

    KINDPAIRS = _ur.DatDict(
        POS = _pkind['POSITIONAL_ONLY'],
        POSKW = _pkind['POSITIONAL_OR_KEYWORD'],
        ARGS = _pkind['VAR_POSITIONAL'],
        KW = _pkind['KEYWORD_ONLY'],
        KWARGS = _pkind['VAR_KEYWORD'],
        )

    __merge_fintyp__ = Fields
    _slotcached_ = True

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        if params.kind is NotImplemented:
            params.kind = 'POSKW'
        elif params.kind not in cls.KINDPAIRS:
            raise ValueError(params.kind)
        if params.hint is NotImplemented:
            params.hint = params.arg
        return params

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
            arg, note, kind = anno
            return cls(arg=arg, note=note, default=value, kind=kind)
        if anno is cls:
            return cls(default=value)
        return cls(arg=anno, default=value)

    def __bound_get__(self, instance, name, /):
        return getattr(instance.params, name)


class FieldAnno:

    def __iter__(self, /):
        return
        yield

    def __repr__(self, /):
        return f"{type(self).__qualname__}({', '.join(map(repr, self))})"


class FieldKind(FieldAnno):

    def __init__(self, /, kind=NotImplemented):
        self.kind = kind

    def __iter__(self, /):
        yield from (NotImplemented, NotImplemented, self.kind)

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, note=note)

    def __getitem__(self, arg, /):
        return FieldHint(kind=self.kind, arg=arg)


with Field.mutable:
    for kindname in Field.KINDPAIRS:
        setattr(Field, kindname, FieldKind(kindname))
del kindname


class FieldHint(FieldAnno):

    def __init__(self, /, kind=NotImplemented, arg=NotImplemented):
        self.kind, self.arg = kind, arg

    def __iter__(self, /):
        yield from (self.arg, NotImplemented, self.kind)

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, arg=self.arg, note=note)


class FieldNote(FieldAnno):

    def __init__(
            self,
            kind=NotImplemented, arg=NotImplemented, note=NotImplemented
            ):
        self.kind, self.arg, self.note = kind, arg, note

    def __iter__(self, /):
        yield from (self.arg, self.note, self.kind)


###############################################################################
###############################################################################
