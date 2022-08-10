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
from .essence import Any as _Any, Null as _Null
from . import ptolemaic as _ptolemaic


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


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
    def _process_hint(cls, hint, /):
        if isinstance(hint, _PathGet):
            return hint
        elif isinstance(hint, type):
            if isinstance(hint, _ptolemaic.Ptolemaic):
                return hint
            raise TypeError(hint)
        if isinstance(hint, str):
            return _PathGet(hint)
        if isinstance(hint, tuple):
            return tuple(map(cls._process_hint, hint))
        if hint is Ellipsis:
            return _Any
        if hint is None:
            return _Null
        if hint is NotImplemented:
            return hint
        raise ValueError(hint)

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        params = super()._parameterise_(*args, **kwargs)
        params.kind = cls._process_kind(params.kind)
        params.hint = cls._process_hint(params.hint)
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

    def __directive_call__(self, body, name, /, content=NotImplemented):
        super().__directive_call__(body, name, content)
        if content is not NotImplemented:
            body[name] = body['comp'](content)
        return name, content

    def __init__(self, /):
        super().__init__()
        degenerate = self.degenerate = False
        if degenerate:
            self.score = -1
        else:
            self.score = sum((
                getattr(self, 'kind', Kind.POSKW).serial,
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
        return lambda inst: inst.__params__[inst._field_indexer(name)]

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
