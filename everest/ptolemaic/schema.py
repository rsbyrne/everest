###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator
import weakref as _weakref

from everest.ptolemaic.tekton import Tekton as _Tekton, Tektoid as _Tektoid
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.sig import (
    Sig as _Sig, Field as _Field
    )


class ParamProp:

    __slots__ = ('name',)

    def __init__(self, name: str, /):
        self.name = name

    def __get__(self, instance, _=None):
        try:
            return instance.params[self.name]
        except KeyError:
            raise AttributeError(self.name)
        except AttributeError:
            return self


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
        for name, note in anno.items():
            deq = fields.setdefault(name, _collections.deque())
            if note is _Field:
                field = note()
            elif isinstance(note, _Field):
                field = note
            else:
                field = _Field[note]
            deq.append(field)
        for base in bases:
            if not isinstance(base, Schema):
                continue
            for name, field in base.sig.fields.items():
                deq = fields.setdefault(name, _collections.deque())
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
        return _Sig(**meta.collect_fields(bases, namespace))

    @classmethod
    def process_namespace(meta, name, bases, namespace):
        namespace = super().process_namespace(name, bases, namespace)
        namespace.update({
            name: _ParamProp(name) for name in namespace['sig'].fields
            })
        return namespace

    def __incise_slyce__(cls, sig, /):
        return Schemoid(cls, sig)

    def __incise_retrieve__(cls, params, /):
        try:
            return (premade := cls.premade)[params]
        except KeyError:
            out = premade[params] = cls.__construct__(params)
            return out

    @classmethod
    def __meta_call__(meta, /, *args, **kwargs):
        return meta.__class_construct__(*args, **kwargs)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.premade = _weakref.WeakValueDictionary()

    def __call__(cls, /, *args, **kwargs):
        return cls.__incise_retrieve__(cls.sig(*args, **kwargs))


class Schemoid(_Tektoid):
    ...


class SchemaBase(metaclass=Schema):

    _req_slots__ = ('params',)

    @classmethod
    def __construct__(cls, params, /):
        obj = object.__new__(cls.Concrete)
        obj.params = params
        obj.__init__()
        obj.freezeattr.toggle(True)
        return obj

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            "$a[$b]",
            a=self._ptolemaic_class__, b=self.params,
            )

    def _repr(self, /):
        return self.hashID

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
