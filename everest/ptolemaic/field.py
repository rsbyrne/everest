###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools

from .smartattr import (
    SmartAttr as _SmartAttr, SmartAttrHolder as _SmartAttrHolder
    )
from .sprite import Sprite as _Sprite
from .pathget import PathGet as _PathGet
from .enumm import Enumm as _Enumm
from .semaphore import Semaphore as _Semaphore
from .essence import Any as _Any
from . import ptolemaic as _ptolemaic


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


class Signal(metaclass=_Enumm):

    MANDATORY: 'Signals a mandatory argument.'

    class SignalCall(metaclass=_Sprite):
        signal: '..'
        content: ...

    @member
    class ANCILLARY(mroclass('.SignalCall')):
        'Signals an ancillary argument.'
        def __call__(self, body, /):
            return self.signal, body['prop'](self.content)

    @member
    class CALLBACK(mroclass('.SignalCall')):
        'Signals a callback argument.'
        def __call__(self, body, /):
            return self.signal, self.content

    def __call__(self, content, /):
        return self.value(self, content)


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
    FIXED: 'A field whose value is fixed.' \
        = _pempty

    def __call__(self, note, /):
        return FieldNote(kind=self, note=note)

    def __getitem__(self, arg, /):
        return FieldHint(kind=self, hint=arg)


class Fields(_SmartAttrHolder):

    __slots__ = ('_signature', 'defaults', 'degenerates')

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        return super()._parameterise_(cls.__content_type__(
            sorted(dict(*args, **kwargs).items(), key=(lambda x: x[1].score))
            ))

    def __init__(self, /):
        super().__init__()
        self.degenerates = {
            name: getattr(field, 'default', NotImplemented)
            for name, field in self.items() if field.degenerate
            }

    def __contains__(self, fieldvals: tuple) -> bool:
        for val, field in zip(fieldvals, self):
            if val not in field:
                return False
        return True

    @property
    def npos(self, /):
        return sum(
            1 if getattr(fld, 'kind', None) is Kind.POS else 0
            for fld in self.values()
            )


class Field(_SmartAttr):

    __slots__ = ('score', 'degenerate')

    default: ... = NotImplemented
    kind: ... = NotImplemented

    __merge_fintyp__ = Fields

    @classmethod
    def _process_kind(cls, kind, /):
        if kind is NotImplemented:
            return kind
        if isinstance(kind, Kind):
            return kind
        return Kind[kind]

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.kind = cls._process_kind(params.kind)
        return params

    @classmethod
    def check_content(cls, params, content, /):
        super().check_content(params, content)

    @classmethod
    def adjust_params_for_content(cls, params, content, /):
        if params.default is NotImplemented:
            params.default = Signal.CALLBACK
            super().adjust_params_for_content(params, content)

    @classmethod
    def _merge_smartattrs(cls, prev, current, /):
        if prev is current:
            return prev
        pairs = tuple(
            tuple(getattr(obj, nm, NotImplemented) for obj in (prev, current))
            for nm in cls.__fields__
            )
        if all(pair[1] is NotImplemented for pair in pairs):
            return prev
        if all(pair[0] is NotImplemented for pair in pairs):
            return current
        return cls(*(
            first if second is NotImplemented else second
            for first, second in pairs
            ))

    # def __directive_call__(self, body, name, /, content=NotImplemented):
    #     super().__directive_call__(body, name, content)
    #     if content is not NotImplemented:
    #         body[name] = body['comp'](content)
    #     return name, content

    def __init__(self, /):
        super().__init__()
        kind = getattr(self, 'kind', Kind.POSKW)
        degenerate = self.degenerate = kind is Kind.FIXED
        if degenerate:
            self.score = -1
        else:
            self.score = sum((
                kind.serial,
                (0.5 if hasattr(self, 'default') else 0),
                ))

    @classmethod
    def _get_parameter_default(cls, kls, default, /):
        if default is Signal.MANDATORY:
            return _pempty
        if default is Signal.ANCILLARY:
            return NotImplemented
        if isinstance(default, _PathGet):
            return default(kls)
        return default

    @classmethod
    def _get_parameter_hint(cls, kls, hint, /):
        if isinstance(hint, tuple):
            return tuple(
                cls._get_parameter_hint(kls, subhint)
                for subhint in hint
                )
        if isinstance(hint, _PathGet):
            return hint(kls)
        return hint

    def get_parameter(self, kls, name, /):
        return _inspect.Parameter(
            name,
            getattr(self, 'kind', Kind.POSKW).value,
            default=self._get_parameter_default(
                kls, getattr(self, 'default', Signal.MANDATORY)
                ),
            annotation=self._get_parameter_hint(
                kls, getattr(self, 'hint', _Any)
                ),
            )

    @classmethod
    def from_annotation(cls, body, name, anno, value):
        if isinstance(value, Signal.SignalCall):
            value, content = value(body)
        else:
            content = None
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
        body[name] = body['field'](content, **kwargs)

    def _get_getter_(self, obj, name, /):
        return lambda inst: getattr(inst.params, name)

    def _get_setter_(self, obj, name, /):
        return super()._get_setter_(None, name)

    def _get_deleter_(self, obj, name, /):
        return super()._get_deleter_(None, name)


with Field.__mutable__:
    for kind in Kind:
        setattr(Field, kind.name, kind)
    del kind


###############################################################################
###############################################################################
