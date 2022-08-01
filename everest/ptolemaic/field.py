###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools

from .smartattr import SmartAttr as _SmartAttr, Get as _Get
from .sprite import Sprite as _Sprite
from .enumm import Enumm as _Enumm


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


class Signal(metaclass=_Enumm):

    MANDATORY: 'Signals a mandatory argument.'
    ANCILLARY: 'Signals an optional argument.'


class FieldHint(metaclass=_Sprite):

    kind: ...
    hint: ...

    def __call__(self, note, /):
        return FieldNote(kind=self.kind, hint=self.hint, note=note)


class FieldNote(metaclass=_Sprite):

    kind: ...
    hint: ...
    note: ...


class Kind(metaclass=_Enumm):

    POS: 'Positional only.' \
        = _pkind['POSITIONAL_ONLY']
    POSKW: 'Positional or keyword.' \
        = _pkind['POSITIONAL_OR_KEYWORD']
    ARGS: 'Gather extra positional arguments.' \
        = _pkind['VAR_POSITIONAL']
    KW: 'Keyword only.' \
        = _pkind['KEYWORD_ONLY']
    KWARGS: 'Gather extra keyword arguments' \
        = _pkind['VAR_KEYWORD']

    def __call__(self, note, /):
        return FieldNote(kind=self, note=note)

    def __getitem__(self, arg, /):
        return FieldHint(kind=self, hint=arg)


class Field(_SmartAttr):

    __slots__ = ('score', 'degenerate')

    default: ... = Signal.MANDATORY
    kind: ... = Kind.POSKW

    __merge_fintyp__ = Fields

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        params = super().__parameterise__(*args, **kwargs)
        if not isinstance(kind := params.kind, Kind):
            params.kind = Kind[kind]
        return params

    @classmethod
    def adjust_params_for_content(cls, params, content, /):
        super().adjust_params_for_content(params, content)
        if params.default is not Signal.MANDATORY:
            raise ValueError(
                "It is forbidden to provide the 'default' argument " 
                "when content is also provided."
                )
        params.default = Signal.ANCILLARY

    def __directive_call__(self, body, name, /, content=NotImplemented):
        super().__directive_call__(body, name, content)
        if content is not NotImplemented:
            body[name] = body['comp'](content)
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
                (0 if default is Signal.MANDATORY else 0.5),
                ))

    def get_parameter(self, kls, name, /):
        default = self.default
        if default is Signal.MANDATORY:
            default = _pempty
        elif default is Signal.ANCILLARY:
            default = NotImplemented
        elif isinstance(default, _Get):
            default = default(kls)
        hint = (hint(kls) if isinstance(hint := self.hint, _Get) else hint)
        return _inspect.Parameter(
            name, self.kind._value_,
            default=default, annotation=hint,
            )

    @classmethod
    def from_annotation(cls, anno, value):
        if isinstance(anno, Kind):
            kwargs = dict(kind=anno)
        elif isinstance(anno, FieldHint):
            kwargs = dict(hint=anno.hint, kind=anno.kind)
        elif isinstance(anno, FieldNote):
            kwargs = dict(hint=anno.hint, note=anno.note, kind=anno.kind)
        elif anno is cls:
            kwargs = dict()
        else:
            kwargs = dict(hint=anno)
        if value is not NotImplemented:
            kwargs['default'] = value
        return cls(**kwargs)

    def _get_getter_(self, obj, name, /):
        return lambda inst: inst.params[inst._field_indexer(name)]

    def _get_setter_(self, obj, name, /):
        return super()._get_setter_(None, name)

    def _get_deleter_(self, obj, name, /):
        return super()._get_deleter_(None, name)


with Field.mutable:
    for kind in Kind:
        setattr(Field, kind.name, kind)
    del kind


###############################################################################
###############################################################################
