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

    __slots__ = ('_signature', 'defaults', 'degenerates')

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
        signature = self._signature = _inspect.Signature(
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
            **self._signature.bind(*args, **kwargs).arguments,
            **self.degenerates
            }.values())

    def __contains__(self, fieldvals: tuple) -> bool:
        for val, field in zip(fieldvals, self):
            if val not in field:
                return False
        return True

    def __get__(self, instance, owner=None, /):
        return self


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
        return params

    @classmethod
    def _instantiate_(cls, params: tuple, /):
        obj = super()._instantiate_(params)
        degen = obj.degenerate = not bool(obj.hint)
        if degen:
            obj.score = -1
        else:
            obj.score = sum((
                tuple(cls.KINDPAIRS).index(obj.kind),
                (0 if obj.default is NotImplemented else 0.5),
                ))
        return obj

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
            return cls.semi_call((hint, note, value, kind))
        if anno is cls:
            return cls.semi_call(default=value)
        return cls.semi_call(hint=anno, default=value)

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        return getattr(instance.params, self.__relname__)


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
