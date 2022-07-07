###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools

from .smartattr import SmartAttr as _SmartAttr
from .sprite import Sprite as _Sprite
from .enumm import Enumm as _Enumm
from .prop import Prop as _Prop


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


class Fields(_SmartAttr.__merge_fintyp__):

    __slots__ = ('_signature', 'defaults', 'degenerates')

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        return super().__parameterise__(cls.__content_type__(
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


class Signals(metaclass=_Enumm):

    MANDATORY: 'Signals a mandatory argument.'
    ANCILLARY: 'Signals an optional argument.'


class Kinds(metaclass=_Enumm):

    POS: 'Positional only.' \
        = _pkind['POSITIONAL_ONLY']
    POSKW: 'Positional or keyword.' \
        = _pkind['POSITIONAL_OR_KEYWORD']
    ARGS: 'Gather extra positional arguments.' \
        = _pkind['VAR_POSITIONAL']
    KW: 'Keyword only.' = \
        _pkind['KEYWORD_ONLY']
    KWARGS: 'Gather extra keyword arguments' = \
        _pkind['VAR_KEYWORD']


class Field(_SmartAttr):

    __slots__ = ('score', 'degenerate')

    default: None = Signals.MANDATORY
    kind: None = Kinds.POSKW

    __merge_fintyp__ = Fields

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        if not isinstance(kind := params.kind, Kinds):
            params.kind = Kinds[kind]
        return params

    @classmethod
    def adjust_params_for_content(cls, params, content, /):
        super().adjust_params_for_content(params, content)
        if params.default is not Signals.MANDATORY:
            raise ValueError(
                "It is forbidden to provide the 'default' argument " 
                "when content is also provided."
                )
        params.default = Signals.ANCILLARY

    def __directive_call__(self, body, name, /, content=NotImplemented):
        body[self.__merge_name__][name] = self
        if content is not NotImplemented:
            body[name] = _Prop.__body_call__(body, content)
        return name, content

    def __init__(self, /):
        super().__init__()
        kind = self.kind
        default = self.default
        degenerate = self.degenerate = False
        if degenerate:
            self.score = -1
        else:
            self.score = sum((
                self.kind.serial,
                (0 if default is Signals.MANDATORY else 0.5),
                ))

    def get_parameter(self, name, /):
        default = self.default
        if default is Signals.MANDATORY:
            default = _pempty
        elif default is Signals.ANCILLARY:
            default = NotImplemented
        return _inspect.Parameter(
            name, self.kind._value_,
            default=default, annotation=self.hint,
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


class FieldAnno(metaclass=_Sprite):

    def __iter__(self, /):
        return
        yield

    def __repr__(self, /):
        return f"{type(self).__qualname__}({', '.join(map(repr, self))})"


class FieldKind(FieldAnno):

    kind: object

    def __iter__(self, /):
        yield from (NotImplemented, NotImplemented, self.kind)

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, note=note)

    def __getitem__(self, arg, /):
        return FieldHint(kind=self.kind, hint=arg)


with Field.mutable:
    for kind in Kinds:
        setattr(Field, kind.name, FieldKind(kind))
    del kind


class FieldHint(FieldAnno):

    kind: object
    hint: object

    def __iter__(self, /):
        yield from (self.hint, NotImplemented, self.kind)

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, hint=self.hint, note=note)


class FieldNote(FieldAnno):

    kind: object
    hint: object
    note: object

    def __iter__(self, /):
        yield from (self.hint, self.note, self.kind)


###############################################################################
###############################################################################
