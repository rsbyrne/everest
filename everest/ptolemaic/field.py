###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools

from .smartattr import SmartAttr as _SmartAttr


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


class Fields(_SmartAttr.__merge_fintyp__):

    __slots__ = ('_signature', 'defaults', 'degenerates')

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return super().parameterise(cls.__content_type__(
            sorted(dict(*args, **kwargs).items(), key=(lambda x: x[1].score))
            ))

    def __init__(self, /):
        super().__init__()
        self.degenerates = {
            name: field.default
            for name, field in self.items() if field.degenerate
            }

    def __contains__(self, fieldvals: tuple) -> bool:
        for val, field in zip(fieldvals, self):
            if val not in field:
                return False
        return True


class Field(_SmartAttr):

    __slots__ = ('score', 'degenerate')

    default: None
    kind: None

    KINDPAIRS = dict(
        POS = _pkind['POSITIONAL_ONLY'],
        POSKW = _pkind['POSITIONAL_OR_KEYWORD'],
        ARGS = _pkind['VAR_POSITIONAL'],
        KW = _pkind['KEYWORD_ONLY'],
        KWARGS = _pkind['VAR_KEYWORD'],
        )

    __merge_fintyp__ = Fields

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        if params.kind is NotImplemented:
            params.kind = 'POSKW'
        elif params.kind not in cls.KINDPAIRS:
            raise ValueError(params.kind)
        return params

    def __init__(self, /):
        super().__init__()
        kind = self.kind
        default = self.default
        degenerate = self.degenerate = False
        if degenerate:
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
            return cls(hint=hint, note=note, default=value, kind=kind)
        if anno is cls:
            return cls(default=value)
        return cls(hint=anno, default=value)

    def _get_getter_(self, obj, name, /):
        return lambda inst: inst.params[inst._field_indexer(name)]

    def _get_setter_(self, obj, name, /):
        return super()._get_setter_(None, name)

    def _get_deleter_(self, obj, name, /):
        return super()._get_deleter_(None, name)

    # def __directive_call__(self, body, name, /):
    #     super().__directive_call__(body, name)
    #     return None, None  # i.e. Field eats the attribute.


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
        return FieldHint(kind=self.kind, hint=arg)


with Field.mutable:
    for kindname in Field.KINDPAIRS:
        setattr(Field, kindname, FieldKind(kindname))
del kindname


class FieldHint(FieldAnno):

    def __init__(self, /, kind=NotImplemented, hint=NotImplemented):
        self.kind, self.hint = kind, hint

    def __iter__(self, /):
        yield from (self.hint, NotImplemented, self.kind)

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, hint=self.hint, note=note)


class FieldNote(FieldAnno):

    def __init__(
            self,
            kind=NotImplemented, hint=NotImplemented, note=NotImplemented
            ):
        self.kind, self.hint, self.note = kind, hint, note

    def __iter__(self, /):
        yield from (self.hint, self.note, self.kind)


###############################################################################
###############################################################################
