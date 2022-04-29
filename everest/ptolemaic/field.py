###############################################################################
''''''
###############################################################################


import abc as _abc
from enum import Enum as _Enum
import inspect as _inspect
import itertools as _itertools

from everest import epitaph as _epitaph
from everest.utilities import pretty as _pretty

from .essence import Essence as _Essence
from .atlantean import Atlantean as _Atlantean


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


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

    _req_slots__ = ('score',)

    @_abc.abstractmethod
    def get_parameter(self, name: str = 'anon', /) -> _pkind:
        raise NotImplementedError

    @staticmethod
    def process_kind(kind, /):
        if isinstance(kind, _pkind):
            return ParamKind.convert(kind)
        if not isinstance(kind, ParamKind):
            raise TypeError(f"Kind must be `ParamKind`.")
        return kind


class FieldKind(FieldBase, metaclass=_Atlantean):

    kind: ParamKind

    _req_slots__ = ('kind',)

    def __init__(self, kind: ParamKind, /, _skipcheck=False):
        if not _skipcheck:
            kind = self.process_kind(kind)
        self.kind = kind
        self.score = kind.score

    def __call__(self, /, *args, **kwargs):
        return Field(self.kind, *args, **kwargs)

    def __getitem__(self, arg, /):
        if not isinstance(arg, FieldBase):
            return Field(self.kind, arg)
        if isinstance(arg, FieldKind):
            kind = max(arg.kind, self.kind)
            return FieldKind(kind)
        if isinstance(arg, Field):
            kind = max(arg.kind, self.kind)
            return Field(kind, arg.hint, arg.value)
        if isinstance(arg, DegenerateField):
            return arg
        raise TypeError(arg)      

    @property
    def get_parameter(self, /):
        return self().get_parameter

    def __str__(self, /):
        return f"FieldKind.{self.kind.name}"

    def _content_repr(self, /):
        return repr(self.kind)

    def make_epitaph(self, /):
        return _epitaph.TAPHONOMY.callsig_epitaph(
            self._ptolemaic_class__, self.kind
            )


with FieldBase.mutable:
    for kind in ParamKind:
        setattr(FieldBase, name := kind.name, FieldKind(ParamKind[name]))


class Field(FieldBase, metaclass=_Atlantean):

    _req_slots__ = ('kind', 'hint', 'value', 'args')

    @staticmethod
    def process_value(value, /):
        if value is _pempty:
            return NotImplemented
        return value

    @staticmethod
    def process_hint(hint, /):
        if hint is _pempty:
            return object
        if isinstance(hint, tuple):
            if len(hint) < 1:
                raise TypeError("Hint cannot be an empty tuple.")
            return hint
        if isinstance(hint, type):
            return hint
        raise TypeError(
            f"The `Field` hint must be a type or a tuple of types"
            )

    @staticmethod
    def combine_hints(hints, /):
        return tuple(_itertools.chain.from_iterable(
            hint if isinstance(hint, tuple) else (hint,) for hint in hints
            ))

    def __init__(self, /,
            kind=ParamKind.POSKW, hint=object, value=NotImplemented,
            _skipcheck=False,
            ):
        if not _skipcheck:
            kind = self.process_kind(kind)
            hint = self.process_hint(hint)
            value = self.process_value(value)
        self.kind, self.hint, self.value = self.args = kind, hint, value
        self.score = kind.score + (0 if value is NotImplemented else 0.5)

    def get_parameter(self, name: str = 'anon', /):
        default = _pempty if (val:=self.value) is NotImplemented else val
        return _inspect.Parameter(
            name, self.kind.value,
            default=default,
            annotation=self.hint,
            )

    def __class_getitem__(cls, arg, /):
        if isinstance(arg, FieldBase):
            return arg
        return cls(hint=arg)

    def __contains__(self, arg, /):
        return isinstance(arg, self.hint)

    def __includes__(self, arg, /):
        return issubclass(arg, self.hint)

    def __getitem__(self, arg, /):
        if not isinstance(arg, FieldBase):
            return self._ptolemaic_class__(
                self.kind,
                self.combine_hints(self.hint, arg),
                self.value,
                )
        if isinstance(arg, Field):
            incval = arg.value
            return self._ptolemaic_class__(
                max(param.kind for param in (self, arg)),
                self.combine_hints((self.hint, arg.hint)),
                (self.value if incval is NotImplemented else incval),
                )
        if isinstance(arg, FieldKind):
            return self._ptolemaic_class__(
                max(param.kind for param in (self, arg)),
                self.hint,
                self.value,
                )
        if isinstance(arg, DegenerateField):
            arg = arg.value
            if arg not in self:
                raise ValueError(arg)
            return DegenerateField(arg)
        raise TypeError(type(arg))

    def _content_repr(self, /):
        return ', '.join(map(repr, self.args))

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty_tuple(self.args, p, cycle, root)

    def make_epitaph(self, /):
        return _epitaph.TAPHONOMY.callsig_epitaph(
            self._ptolemaic_class__, *self.args
            )


@FieldBase.register
class DegenerateField(metaclass=_Atlantean):

    _req_slots__ = ('value',)

    score = -1

    def __init__(self, value, /):
        self.value = value

    def retrieve(self, /):
        return self.value

    def get_parameter(self, name: str = 'anon', /):
        return NotImplemented

    def __contains__(self, arg, /):
        return arg == self.value

    def __includes__(self, arg, /):
        if isinstance(arg, DegenerateField):
            return arg.value in self
        return False

    def __getitem__(self, arg, /):
        if isinstance(arg, DegenerateField):
            arg = arg.value
            if arg in self:
                return self
        raise ValueError(arg)

    def _content_repr(self, /):
        return repr(self.value)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty(self.value, p, cycle, root)

    def make_epitaph(self, /):
        return _epitaph.TAPHONOMY.callsig_epitaph(
            self._ptolemaic_class__, self.value
            )


###############################################################################
###############################################################################
