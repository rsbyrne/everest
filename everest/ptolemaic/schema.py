###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import collections as _collections
import operator as _operator

from everest.ptolemaic.tekton import Tekton as _Tekton
from everest.ptolemaic.ousia import Ousia as _Ousia, OusiaBase as _OusiaBase
from everest.ptolemaic.sig import (
    Sig as _Sig, Field as _Field, ParamProp as _ParamProp
    )


class ConcreteMeta(_Ousia):

    @classmethod
    def _pleroma_construct(meta, basecls):
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if issubclass(type(basecls), ConcreteMeta):
            raise TypeError("Cannot subclass a Concrete type.")
        namespace = dict(
            __slots__=basecls._req_slots__,
            _basecls=basecls,
            __class_init__=lambda: None,
            )
        concretecls = meta.__new__(
            meta,
#             f"Concrete{basecls.__name__}",
            basecls.__name__,
            (basecls, _OusiaBase),
            namespace,
            )
        _abc.ABCMeta.__init__(meta, concretecls)
        return concretecls

    @property
    def __signature__(cls, /):
        return cls._ptolemaic_class__.__signature__

    @property
    def _ptolemaic_class__(cls, /):
        return cls._basecls


def get_field_value(bases, namespace, name, /):
    if name in namespace:
        return namespace[name]
    for base in bases:
        if hasattr(base, name):
            return getattr(base, name)
    return NotImplemented

def collect_fields(bases, namespace, /):
    fields = dict()
    anno = namespace['__annotations__']
    for name, note in anno.items():
        deq = fields.setdefault(name, _collections.deque())
        if note is _Field:
            field = note()
        elif isinstance(note, _Field):
            field = note
        else:
            field = _Field(note)
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
        value = get_field_value(bases, namespace, name)
        if value is not NotImplemented:
            field = field(value)
        fields[name] = field
    return fields


class Schema(_Tekton):

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
        if not issubclass(meta, ConcreteMeta):
            meta.ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (ConcreteMeta, meta),
                {},
                )

    @classmethod
    def get_signature(meta, name, bases, namespace, /):
        return _Sig(**collect_fields(bases, namespace))

    @classmethod
    def pre_create_class(meta, name, bases, namespace):
        super().pre_create_class(name, bases, namespace)
        namespace.update({
            name: _ParamProp(name) for name in namespace['sig'].fields
            })

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        conc = cls.Concrete = cls.ConcreteMeta(cls)
        cls.construct = conc.__class_call__


class SchemaBase(metaclass=Schema):

    MERGETUPLES = ('_req_slots__',)
    _req_slots__ = ('params',)

    def initialise(self, params, /, *args, **kwargs):
        self.params = params
        super().initialise(*args, **kwargs)

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            "$a[b]",
            a=self._ptolemaic_class__, b=self.params,
            )

    def _repr(self, /):
        return str(self.params)


###############################################################################
###############################################################################


# class MyClass(metaclass=Schema):
#     a: Param.Pos[int]
#     b: Param.Pos[float] = 2.
#     c: int = 3
#     args: Param.Args
#     d: Param.Kw[int]
#     kwargs: Param.Kwargs
