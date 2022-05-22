###############################################################################
''''''
###############################################################################


import inspect as _inspect
import types as _types
from collections import namedtuple as _namedtuple

from everest.utilities import pretty as _pretty

from .ousia import (
    Ousia as _Ousia,
    ProvisionalParams as _ProvisionalParams,
    paramstuple as _paramstuple,
    )
from .sprite import Sprite as _Sprite, Kwargs as _Kwargs


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


class SmartAttr(metaclass=_Sprite):

    MERGENAMES = ('__process_params__',)
    __params__ = ('name', 'hint', 'note', 'default')
    __defaults__ = tuple(NotImplemented for key in __params__)
    __req_slots__ = ('cachedname', 'degenerate')

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        for name in cls.__params__:
            params[name] = getattr(cls, f"process_{name}")(params[name])
        return params

    @classmethod
    def convert(cls, arg, /):
        if isinstance(arg, cls):
            return arg
        raise TypeError(type(arg))

    @staticmethod
    def process_name(name, /):
        return str(name)

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
        if isinstance(hint, str):
            return hint
        raise TypeError(
            f"The `Field` hint must be a type or a tuple of types:",
            hint,
            )

    @staticmethod
    def process_note(note, /):
        if note is _pempty:
            return ''
        return str(note)

    @staticmethod
    def process_default(default, /):
        if default is _pempty:
            return NotImplemented
        return default

    def __init__(self, /):
        self.cachedname = f"_cached_{self.name}"
        self.degenerate = not bool(self.hint)


class Prop(SmartAttr):

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        return instance.__getattribute__(self.cachedname, self.default)

    def __set__(self, instance, value, /):
        setattr(instance, self.cachedname, value)


class Field(SmartAttr):

    __params__ = ('kind',)
    __defaults__ = tuple(NotImplemented for key in __params__)
    __req_slots__ = ('score', 'parameter')

    KINDPAIRS = _types.MappingProxyType(dict(
        POS = _pkind['POSITIONAL_ONLY'],
        POSKW = _pkind['POSITIONAL_OR_KEYWORD'],
        ARGS = _pkind['VAR_POSITIONAL'],
        KW = _pkind['KEYWORD_ONLY'],
        KWARGS = _pkind['VAR_KEYWORD'],
        ))

    @classmethod
    def process_kind(cls, kind, /):
        if kind in (_pempty, NotImplemented):
            return 'POSKW'
        print(kind, type(kind))
        if kind not in cls.KINDPAIRS:
            raise ValueError(kind)
        return kind

    def __init__(self, /):
        super().__init__()
        kind = self.kind
        kindpairs = self.KINDPAIRS
        default = self.default
        if self.degenerate:
            self.score = -1
        else:
            self.score = sum((
                tuple(kindpairs).index(kind),
                (0 if default is NotImplemented else 0.5),
                ))
        self.parameter = _inspect.Parameter(
            self.name, kindpairs[kind],
            default=_pempty if (val:=default) is NotImplemented else val,
            annotation=self.hint,
            )

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        return getattr(instance.params, self.cachedname, self.default)

    def __class_getitem__(cls, arg, /):
        return FieldHint('POSKW', arg)

    @classmethod
    def from_annotation(cls, name, anno, value):
        if isinstance(anno, FieldAnno):
            anno = tuple(anno)
        if isinstance(anno, tuple):
            return cls(name, *anno, default=value)
        if anno is cls:
            return cls(name, default=value)
        return Field(name=name, hint=anno, default=value)


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
        yield self.kind

    def __call__(self, note, /):
        return FieldNote(*self, note=note)

    def __getitem__(self, hint, /):
        return FieldHint(*self, hint)


with Field.mutable:
    for kindname in Field.KINDPAIRS:
        setattr(Field, kindname, FieldKind(kindname))
del kindname     


class FieldHint(FieldAnno):

    def __init__(self, /, kind=_pempty, hint=_pempty):
        self.kind, self.hint = kind, hint

    def __iter__(self, /):
        yield from (self.kind, self.hint)

    def __call__(self, note, /):
        return FieldNote(*self, note)


class FieldNote(FieldAnno):

    def __init__(self, kind=_pempty, hint=_pempty, note=_pempty):
        self.kind, self.hint, self.note = kind, hint, note

    def __iter__(self, /):
        yield from (self.kind, self.hint, self.note)


class Fields(_Kwargs):

    __req_slots__ = ('signature', 'defaults', 'degenerates')

    @classmethod
    def get_orderscore(cls, pair):
        return pair[1].score

    @classmethod
    def sort_fields(cls, fields: dict, /):
        return dict(sorted(fields.items(), key=cls.get_orderscore))

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        (content,) = super().parameterise(*args, **kwargs)
        return (cls.__content_type__(cls.sort_fields(content)),)

    def __init__(self, /):
        degenerates = self.degenerates = _types.MappingProxyType({
            name: field.default
            for name, field in self.items()
            if field.degenerate
            })
        signature = self.signature = _inspect.Signature(
            field.parameter
            for name, field in self.items()
            if name not in degenerates
            )
        self.defaults = _types.MappingProxyType({
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
        for val, field in zip(fieldvals, self.values()):
            if val not in field:
                return False
        return True


class Comp(SmartAttr):
    ...


class Armature(_Ousia):

    @classmethod
    def process_annotations(meta, ns, /):
        annos = super().process_annotations(ns)
        ns.update({
            name: Field.from_annotation(name, annotation, value)
            for name, (annotation, value) in annos.items()
            })
        annos.clear()
        return annos

    @classmethod
    def _yield_namespace_categories(meta, ns, /):
        yield '__props__', Prop.__instancecheck__, ns.get('__props__', {})
        yield '__fields__', Field.__instancecheck__, ns.get('__fields__', {})
        yield '__comps__', Comp.__instancecheck__, ns.get('__comps__', {})

    @classmethod
    def pre_create_class(meta, name, bases, ns, /):
        name, bases, ns = super().pre_create_class(name, bases, ns)
        for cat in (
                ns[name] for name in ('__props__', '__fields__', '__comps__')
                ):
            if not all(val.name == key for key, val in cat.items()):
                raise RuntimeError(
                    "Names of `SmartAttrs` must match their assigned names."
                    )
            ns.update(cat)
        return name, bases, ns


class ArmatureBase(metaclass=Armature):

    __req_slots__ = ('params',)
    MERGENAMES = (
        ('__props__', _Kwargs),
        ('__fields__', Fields),
        ('__comps__', _Kwargs),
        )

    @classmethod
    def _make_params_type(cls, /):
        fields = cls.__fields__
        return _paramstuple(cls.__name__, fields, defaults=fields.defaults)

    @classmethod
    def _get_signature(cls, /):
        return cls.__fields__.signature

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from cls.__req_slots__
        yield from (prop.cachedname for prop in cls.__props__.values())

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return _ProvisionalParams(
            cls.__signature__.bind(*args, **kwargs).arguments
            )


###############################################################################
###############################################################################



# class Comp(SmartAttr, metaclass=_Ousia):

#     __req_slots__ = ('fget',)

#     @classmethod
#     def __class_call__(cls, arg, /):
#         if cls is not Comp:
#             return super().__class_call__(arg)
#         if isinstance(arg, str, /):
#             return EvalComp(arg)
#         return FuncComp()

#     def __get__(self, instance, owner=None, /):
#         name = f"_cached_{self.name}"
#         try:
#             return getattr(instance, name)
#         except AttributeError:
#             out = self.func(instance)
#             setattr(instance, name, out)
#             return out

#     def __class_getitem__(cls, arg: tuple, /):
#         if cls is not Comp:
#             raise AttributeError
#         hint, note = arg
#         return _functools.partial()


# class EvalComp(Comp):

#     __req_slots__ = ('evalstr', 'returns', 'note')

#     def __init__(self,
#             evalstr: str, returns: type = object, note: str = '', /
#             ):
#         self.evalstr = evalstr
#         self.fget = lambda: eval(evalstr)
#         self.returns = returns
#         self.note = note

#     def make_epitaph(self, /):
#         return _epitaph.TAPHONOMY.callsig_epitaph(
#             self.__ptolemaic_class__, self.evalstr, self.returns, self.note
#             )


# class FuncComp(Comp):

#     def __init__(self, func: _types.FunctionType):
#         self.fget = func

#     @property
#     def returns(self, /):
#         return self.func.__annotations__.get('return', '')

#     @property
#     def note(self, /):
#         return self.func.__doc__

#     def make_epitaph(self, /):
#         return _epitaph.TAPHONOMY.callsig_epitaph(
#             self.__ptolemaic_class__, self.fget
#             )


# class SmartAttr(metaclass=_Ousia):

#     __req_slots__ = ('owner', 'nameset', 'name')

    

#     def __set_name__(self, owner, name, /):
#         if self.nameset:
#             raise RuntimeError("Cannot reset name on Comp.")
#         with self.mutable:
#             self.owner, self.nameset, self.name = owner, True, name

#     def make_epitaph(self, /):
#         if not self.nameset:
#             raise RuntimeError("Cannot make epitaph from unbound Comp.")
#         return _epitaph.TAPHONOMY.getattr_epitaph(
#             self.owner, self.name,
#             )


# @OusiaBase.register
# class Kind(_Enum):

#     POS = _pkind['POSITIONAL_ONLY']
#     POSKW = _pkind['POSITIONAL_OR_KEYWORD']
#     ARGS = _pkind['VAR_POSITIONAL']
#     KW = _pkind['KEYWORD_ONLY']
#     KWARGS = _pkind['VAR_KEYWORD']

#     __slots__ = ('_epitaph',)

#     def __repr__(self, /):
#         return f"<Kind[{self.name}]>"

#     @property
#     def epitaph(self, /):
#         try:
#             return self._epitaph
#         except AttributeError:
#             epi = self._epitaph = _epitaph.TAPHONOMY.custom_epitaph(
#                 "$A[$a]", A=Kind, a=self.name
#                 )
#             return epi

#     @classmethod
#     def convert(cls, arg, /):
#         if isinstance(arg, cls):
#             return arg
#         if isinstance(arg, str):
#             return cls[arg]
#         if isinstance(arg, _pkind):
#             return tuple(cls)[arg.value]
#         raise TypeError("Cannot convert to `Kind`.")

#     @property
#     def score(self, /):
#         return self.value.value

#     def __gt__(self, other, /):
#         return self.score > other.score

#     def __lt__(self, other, /):
#         return self.score < other.score

#     def __ge__(self, other, /):
#         return self.score >= other.score

#     def __le__(self, other, /):
#         return self.score <= other.score

#     def __eq__(self, other, /):
#         return self.score == other.score

#     def __ne__(self, other, /):
#         return self.score != other.score

#     def __hash__(self, /):
#         return self.epitaph.hashint


# class FieldBase(metaclass=_Essence):

#     __req_slots__ = ('score',)

#     @_abc.abstractmethod
#     def get_parameter(self, name: str = 'anon', /) -> _pkind:
#         raise NotImplementedError

#     @staticmethod
#     def process_kind(kind, /):
#         if isinstance(kind, _pkind):
#             return Kind.convert(kind)
#         if not isinstance(kind, Kind):
#             raise TypeError(f"Kind must be `Kind`.")
#         return kind


# class FieldKind(FieldBase, metaclass=_Ousia):

#     __req_slots__ = ('kind',)

#     def __init__(self, kind: Kind, /, _skipcheck=False):
#         if not _skipcheck:
#             kind = self.process_kind(kind)
#         self.kind = kind
#         self.score = kind.score

#     def __call__(self, /, *args, **kwargs):
#         return Field(self.kind, *args, **kwargs)

#     def __getitem__(self, arg, /):
#         if not isinstance(arg, FieldBase):
#             return Field(self.kind, arg)
#         if isinstance(arg, FieldKind):
#             kind = max(arg.kind, self.kind)
#             return FieldKind(kind)
#         if isinstance(arg, Field):
#             kind = max(arg.kind, self.kind)
#             return Field(kind, arg.hint, arg.note, arg.value)
#         if isinstance(arg, DegenerateField):
#             return arg
#         raise TypeError(arg)

#     @property
#     def get_parameter(self, /):
#         return self().get_parameter

#     def __str__(self, /):
#         return f"FieldKind.{self.kind.name}"

#     def _content_repr(self, /):
#         return repr(self.kind)

#     def make_epitaph(self, /):
#         return _epitaph.TAPHONOMY.callsig_epitaph(
#             self.__ptolemaic_class__, self.kind
#             )


# with FieldBase.mutable:
#     for kind in Kind:
#         setattr(FieldBase, name := kind.name, FieldKind(Kind[name]))


# class Field(FieldBase, SmartAttr):

#     __req_slots__ = ('kind', 'hint', 'note', 'value', 'args')

#     @staticmethod
#     def process_hint(hint, /):
#         if hint is _pempty:
#             return object
#         if isinstance(hint, tuple):
#             if len(hint) < 1:
#                 raise TypeError("Hint cannot be an empty tuple.")
#             return hint
#         if isinstance(hint, type):
#             return hint
#         if isinstance(hint, str):
#             return hint
#         raise TypeError(
#             f"The `Field` hint must be a type or a tuple of types:",
#             hint,
#             )

#     @staticmethod
#     def process_note(note, /):
#         return str(note)

#     @staticmethod
#     def process_value(value, /):
#         if value is _pempty:
#             return NotImplemented
#         return value

#     @staticmethod
#     def combine_hints(hints, /):
#         return tuple(_itertools.chain.from_iterable(
#             hint if isinstance(hint, tuple) else (hint,) for hint in hints
#             ))

#     @staticmethod
#     def combine_notes(notes, /):
#         return '; '.join(notes)

#     def __init__(self, /,
#             kind=Kind.POSKW, hint=object, note='', value=NotImplemented,
#             _skipcheck=False,
#             ):
#         if not _skipcheck:
#             kind = self.process_kind(kind)
#             hint = self.process_hint(hint)
#             note = self.process_note(note)
#             value = self.process_value(value)
#         self.kind, self.hint, self.note, self.value = self.args = \
#             kind, hint, note, value
#         self.score = kind.score + (0 if value is NotImplemented else 0.5)

#     def get_parameter(self, name: str = 'anon', /):
#         default = _pempty if (val:=self.value) is NotImplemented else val
#         return _inspect.Parameter(
#             name, self.kind.value,
#             default=default,
#             annotation=self.hint,
#             )

#     def __class_getitem__(cls, arg, /):
#         if isinstance(arg, FieldBase):
#             return arg
#         return cls(hint=arg)

#     def __contains__(self, arg, /):
#         return isinstance(arg, self.hint)

#     def __includes__(self, arg, /):
#         return issubclass(arg, self.hint)

#     def __getitem__(self, arg, /):
#         if not isinstance(arg, FieldBase):
#             return self.__ptolemaic_class__(
#                 self.kind,
#                 self.combine_hints(self.hint, arg),
#                 self.note,
#                 self.value,
#                 )
#         if isinstance(arg, Field):
#             incval = arg.value
#             return self.__ptolemaic_class__(
#                 max(param.kind for param in (self, arg)),
#                 self.combine_hints((self.hint, arg.hint)),
#                 self.combine_notes((self.note, arg.note)),
#                 (self.value if incval is NotImplemented else incval),
#                 )
#         if isinstance(arg, FieldKind):
#             return self.__ptolemaic_class__(
#                 max(param.kind for param in (self, arg)),
#                 self.hint,
#                 self.note,
#                 self.value,
#                 )
#         if isinstance(arg, DegenerateField):
#             arg = arg.value
#             if arg not in self:
#                 raise ValueError(arg)
#             return DegenerateField(arg)
#         raise TypeError(type(arg))       

#     def _content_repr(self, /):
#         return ', '.join(map(repr, self.args))

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.rootrepr
#         _pretty.pretty_tuple(self.args, p, cycle, root)

#     def __get__(self, instance, /):
#         return getattr(instance.params, self.name)

#     def make_epitaph(self, /):
#         return _epitaph.TAPHONOMY.callsig_epitaph(
#             self.__ptolemaic_class__, *self.args
#             )


# @FieldBase.register
# class DegenerateField(metaclass=_Ousia):

#     __req_slots__ = ('value',)

#     score = -1

#     def __init__(self, value, /):
#         self.value = value

#     def retrieve(self, /):
#         return self.value

#     def get_parameter(self, name: str = 'anon', /):
#         return NotImplemented

#     def __contains__(self, arg, /):
#         return arg == self.value

#     def __includes__(self, arg, /):
#         if isinstance(arg, DegenerateField):
#             return arg.value in self
#         return False

#     def __getitem__(self, arg, /):
#         if isinstance(arg, DegenerateField):
#             arg = arg.value
#             if arg in self:
#                 return self
#         raise ValueError(arg)

#     def _content_repr(self, /):
#         return repr(self.value)

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.rootrepr
#         _pretty.pretty(self.value, p, cycle, root)

#     def make_epitaph(self, /):
#         return _epitaph.TAPHONOMY.callsig_epitaph(
#             self.__ptolemaic_class__, self.value
#             )
