###############################################################################
''''''
###############################################################################


import inspect as _inspect
import types as _types
from collections import abc as _collabc
import itertools as _itertools
import functools as _functools

from everest.utilities import pretty as _pretty
from everest import ur as _ur

from .pentheros import (
    Pentheros as _Pentheros,
    ProvisionalParams as _ProvisionalParams,
    paramstuple as _paramstuple,
    )
from .sprite import Sprite as _Sprite, Tuuple as _Tuuple


_pkind = _inspect._ParameterKind
_pempty = _inspect._empty


class SmartAttr(metaclass=_Sprite):

    __params__ = ('name', 'hint', 'note')
    __defaults__ = tuple(NotImplemented for key in __params__)
    __req_slots__ = ('cachedname', 'degenerate')

    MERGETYPE = _ur.DatTuple

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._mergename = f"__{cls.__name__.lower()}s__"

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
        if name in (_pempty, NotImplemented):
            return 'anon'
        return str(name)

    @staticmethod
    def process_hint(hint, /):
        if hint in (_pempty, NotImplemented):
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
        if note in (_pempty, NotImplemented):
            return '?'
        return str(note)

    def __init__(self, /):
        super().__init__()
        self.cachedname = f"_cached_{self.name}"
        self.degenerate = not bool(self.hint)

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        return getattr(instance, self.cachedname, self.default)


class Fields(_Tuuple):

    __req_slots__ = ('signature', 'defaults', 'degenerates')

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        (fields,) = super().parameterise(*args, **kwargs)
        return (cls.__content_type__(sorted(fields, key=(lambda x: x.score))),)

    def __init__(self, /):
        super().__init__()
        degenerates = self.degenerates = _ur.DatDict({
            field.name: field.default
            for field in self if field.degenerate
            })
        signature = self.signature = _inspect.Signature(
            field.parameter for field in self if field.name not in degenerates
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


class Field(SmartAttr):

    __params__ = ('default', 'kind',)
    __defaults__ = tuple(NotImplemented for key in __params__)
    __req_slots__ = ('score', 'parameter')

    MERGETYPE = Fields

    KINDPAIRS = _ur.DatDict(
        POS = _pkind['POSITIONAL_ONLY'],
        POSKW = _pkind['POSITIONAL_OR_KEYWORD'],
        ARGS = _pkind['VAR_POSITIONAL'],
        KW = _pkind['KEYWORD_ONLY'],
        KWARGS = _pkind['VAR_KEYWORD'],
        )

    @staticmethod
    def process_default(default, /):
        if default is _pempty:
            return NotImplemented
        return default

    @classmethod
    def process_kind(cls, kind, /):
        if kind in (_pempty, NotImplemented):
            return 'POSKW'
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

    def __class_getitem__(cls, arg, /):
        return FieldHint('POSKW', arg)

    @classmethod
    def from_annotation(cls, name, anno, value):
        if isinstance(anno, FieldAnno):
            hint, note, kind = anno
            return cls(name, hint, note, value, kind)
        if anno is cls:
            return cls(name, default=value)
        return cls(name, anno, default=value)

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        return getattr(instance.params, self.name)

    def __set__(self, instance, value, /):
        pass


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


class Tekton(_Pentheros):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield Field

    @classmethod
    def __meta_init__(meta, /):
        super().__meta_init__()
        typs = meta._smartattrtypes = tuple(meta._yield_smartattrtypes())
        for typ in typs:
            setattr(meta, typ.__name__, typ)

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
    def _yield_namespace_categories(meta, /):
        for typ in meta._smartattrtypes:
            yield (typ._mergename, typ.__instancecheck__)

    @classmethod
    def _categorise_namespace(meta, ns, /):
        nms = tuple(typ._mergename for typ in meta._smartattrtypes)
        pre = tuple(ns.pop(nm, ()) for nm in nms)
        super()._categorise_namespace(ns)
        for tup, nm in zip(pre, nms):
            ns[nm] = _ur.DatTuple((*tup, *ns[nm].values()))

    @classmethod
    def process_mergenames(meta, bases, ns, /):
        super().process_mergenames(bases, ns)
        for typ in meta._smartattrtypes:
            meta.process_mergename(bases, ns, (typ._mergename, typ.MERGETYPE))

    @classmethod
    def pre_create_class(meta, name, bases, ns, /):
        name, bases, ns = super().pre_create_class(name, bases, ns)
        for typ in meta._smartattrtypes:
            ns.update({sm.name: sm for sm in ns[typ._mergename]})
        return name, bases, ns

    @classmethod
    def _yield_special_bodyitems(meta, body, /):
        yield from super()._yield_special_bodyitems(body)
        for typ in meta._smartattrtypes:
            nm = typ.__name__.lower()
            try:
                meth = getattr(meta, nm)
            except AttributeError:
                continue
            yield nm, _functools.partial(meth, body)

    @classmethod
    def _smartattr_namemangle(meta, body, arg, /):
        nm = arg.__name__
        if nm.startswith('_'):
            raise RuntimeError(
                "Smart Attribute name cannot start with an underscore."
                )
        altname = f'_{nm}'
        body.safe_set(altname, arg)
        return nm, altname

    @classmethod
    def field(meta, body, arg: Field = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.field, body, **kwargs)
        nm, altname = meta._smartattr_namemangle(body, arg)
        return meta.Field(nm, altname, **kwargs)


class TektonBase(metaclass=Tekton):

    @classmethod
    def _make_params_type(cls, /):
        return _paramstuple(cls.__name__, (fld.name for fld in cls.__fields__))

    @classmethod
    def _get_signature(cls, /):
        return cls.__fields__.signature

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return _ProvisionalParams(bound.arguments)


###############################################################################
###############################################################################
