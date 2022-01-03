###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator

from everest.ptolemaic.tekton import Tekton as _Tekton
from everest.ptolemaic.ousia import Ousia as _Ousia, OusiaBase as _OusiaBase
# from everest.ptolemaic.ptolemaic import (
#     Ptolemaic as _Ptolemaic,
#     PtolemaicBase as _PtolemaicBase,
#     )
from everest.ptolemaic.sig import (
    Sig as _Sig, Field as _Field, ParamProp as _ParamProp
    )


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
        value = get_field_value(bases, namespace, name)
        if value is not NotImplemented:
            field = field(value)
        fields[name] = field
    return fields


class Schema(_Tekton, _Ousia):

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
        cls.construct = cls.Concrete


class SchemaBase(metaclass=Schema):

    CACHE = True

    _req_slots__ = ('params',)

    class ConcreteBase:

        def initialise(self, params, /, *args, **kwargs):
            self.params = params
            super().initialise(*args, **kwargs)

        def get_epitaph(self, /):
            return self.taphonomy.custom_epitaph(
                "$a.retrieve($b)",
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
