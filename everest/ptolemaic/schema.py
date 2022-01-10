###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator
import weakref as _weakref
import types as _types
import inspect as _inspect

from everest.utilities import caching as _caching, reseed as _reseed

from everest.ptolemaic.tekton import Tekton as _Tekton, Tektoid as _Tektoid
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.sig import (
    Sig as _Sig,
    Field as _Field,
    FieldKind as _FieldKind,
    Params as _Params,
    Param as _Param,
    )


class Schema(_Ousia, _Tekton):

    @classmethod
    def get_field_value(meta, bases, namespace, name, /):
        if name in namespace:
            return namespace[name]
        for base in bases:
            if hasattr(base, name):
                return getattr(base, name)
        return NotImplemented

    @classmethod
    def collect_fields(meta, bases, namespace, /):
        fields = dict()
        anno = namespace['__annotations__']
        for base in reversed(bases):
            if not isinstance(base, Schema):
                continue
            for name, field in base.fields.items():
                deq = fields.setdefault(name, _collections.deque())
                deq.append(field)
        for name, note in anno.items():
            deq = fields.setdefault(name, _collections.deque())
            if note is _Field:
                field = note()
            elif isinstance(note, (_Field, _FieldKind)):
                field = note
            else:
                field = _Field[note]
            deq.append(field)
        for name, deq in tuple(fields.items()):
            if len(deq) == 1:
                field = deq[0]
            else:
                field = _functools.reduce(_operator.getitem, reversed(deq))
            value = meta.get_field_value(bases, namespace, name)
            if value is not NotImplemented:
                field = field(value)
            fields[name] = field
        return fields

    @classmethod
    def get_signature(meta, name, bases, namespace, /):
        fields = namespace['fields'] = _types.MappingProxyType(
            meta.collect_fields(bases, namespace)
            )
        return _Sig(**fields)

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    @classmethod
    def pre_create_class(meta, /, *args):
        name, bases, namespace = super().pre_create_class(*args)
        namespace.update({
            name: _Param(name) for name in namespace['fields']
            })
        return name, bases, namespace

    @classmethod
    def __meta_call__(meta, /, *args, **kwargs):
        return meta.__class_construct__(*args, **kwargs)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls.CACHE:
            cls.premade = _weakref.WeakValueDictionary()
            cls.__class_incise_retrieve__ = cls.__cache_construct__
        else:
            cls.__class_incise_retrieve__ = cls.__construct__

    def __call__(cls, /, *args, **kwargs):
        out = cls.__incise_retrieve__(_Params(cls.parameterise(
            cache := {}, *args, **kwargs
            )))
        out.softcache.update(cache)
        return out


class Schemoid(_Tektoid):
    ...


class SchemaBase(metaclass=Schema):

    _req_slots__ = ('params',)

    CACHE = False

    @classmethod
    def __class_incise_slyce__(cls, sig, /):
        return Schemoid(cls, sig)

    @classmethod
    def __cache_construct__(cls, params, /):
        try:
            return (premade := cls.premade)[(hashID := params.hashID)]
        except KeyError:
            out = premade[hashID] = cls.__construct__(params)
            return out

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        return bound

    @classmethod
    def __construct__(cls, params, /):
        obj = object.__new__(cls.Concrete)
        obj.params = params
        obj.__init__()
        obj.freezeattr.toggle(True)
        return obj

    ### Serialisation

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            "$a[$b]",
            a=self._ptolemaic_class__, b=self.params,
            )

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.get_epitaph()

    ### Representations:

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def _repr(self, /):
        return self.hashID

    @_caching.soft_cache()
    def __hash__(self, /):
        return _reseed.rdigits(12)

    def _repr_pretty_(self, p, cycle):
        p.text('<')
        root = repr(self._ptolemaic_class__)
        if cycle:
            p.text(root + '{...}')
        elif not (kwargs := self.params):
            p.text(root + '()')
        else:
            with p.group(4, root + '(', ')'):
                kwargit = iter(kwargs.items())
                p.breakable()
                key, val = next(kwargit)
                p.text(key)
                p.text(' = ')
                p.pretty(val)
                for key, val in kwargit:
                    p.text(',')
                    p.breakable()
                    p.text(key)
                    p.text(' = ')
                    p.pretty(val)
                p.breakable()
        p.text('>')


###############################################################################
###############################################################################
