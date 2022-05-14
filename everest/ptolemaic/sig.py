###############################################################################
''''''
###############################################################################


import inspect as _inspect
import functools as _functools
import operator as _operator
from collections import deque as _deque
import types as _types

from everest import epitaph as _epitaph
from everest.utilities import caching as _caching, pretty as _pretty

from .essence import Essence as _Essence
from .atlantean import Atlantean as _Atlantean
from . import field as _field


_pempty = _inspect._empty


class Sig(metaclass=_Atlantean):

    __req_slots__ = ('sigfields',)

    @classmethod
    def get_orderscore(cls, pair):
        return pair[1].score

    @classmethod
    def sort_fields(cls, fields):
        return dict(sorted(fields.items(), key=cls.get_orderscore))

    @classmethod
    def process_sigfield(cls, name, hint, value, /) -> _field.FieldBase:
        if not isinstance(hint, _field.FieldBase):
            return _field.Field(hint=hint, value=value)
        if isinstance(hint, _field.FieldKind):
            return _field.Field(kind=hint.kind, value=value)
        if isinstance(hint, _field.Field):
            if value is _pempty:
                return hint
            return _field.Field(hint.kind, hint.hint, value)
        if isinstance(hint, _field.DegenerateField):
            if value is not _pempty:
                raise TypeError(name, hint, value)
            return hint
        raise TypeError(type(hint))

    @classmethod
    def sub_gather_fields(cls, bases: iter, fields: dict, /) -> dict:
        try:
            base = next(bases)
        except StopIteration:
            return
        cls.sub_gather_fields(bases, fields)
        anno = base.__dict__.get('__annotations__', {})
        for name, hint in anno.items():
            fields.setdefault(name, _deque()).append(
                cls.process_sigfield(
                    name, hint, base.__dict__.get(name, _pempty)
                    )
                )

    @classmethod
    def gather_fields(cls, typ):
        fields = {}
        baseit = (base for base in typ.__mro__ if isinstance(base, _Essence))
        cls.sub_gather_fields(baseit, fields)
        for name, deq in tuple(fields.items()):
            if len(deq) == 1:
                field = deq[0]
            else:
                field = _functools.reduce(_operator.getitem, deq)
            if isinstance(field, _field.FieldKind):
                field = field[_pempty]
            fields[name] = field
        return cls.sort_fields(fields)

    def __init__(self, arg=None, /, **kwargs):
        cache = {}
        if arg is None:
            fields = self.sort_fields({
                key: field() if isinstance(field, _field.FieldKind) else field
                for key, field in kwargs.items()
                })
        else:
            if kwargs:
                raise TypeError
            if isinstance(arg, dict):
                fields = {
                    key: self.process_sigfield(key, val, _pempty)
                    for key, val in fields.items()
                    }
            elif isinstance(arg, type):
                fields = self.gather_fields(arg)
            else:
                if isinstance(arg, _inspect.Signature):
                    signature = arg
                else:
                    signature = _inspect.signature(arg)
                cache['signature'] = signature
                fields = {
                    pm.name: _field.Field(pm.kind, pm.annotation, pm.default)
                    for pm in signature.parameters.values()
                    }
        self.sigfields = _types.MappingProxyType(fields)
        self.softcache.update(cache)

    @property
    @_caching.soft_cache()
    def signature(self, /):
        return _inspect.Signature(
            field.get_parameter(name)
            for name, field in self.sigfields.items()
            if name not in self.degenerates
            )

    @property
    @_caching.soft_cache()
    def degenerates(self, /):
        return _types.MappingProxyType({
            name: field.retrieve()
            for name, field in self.sigfields.items()
            if isinstance(field, _field.DegenerateField)
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

    for methname in ('keys', 'values', 'items'):
        exec('\n'.join((
            f'@property',
            f'def {methname}(self, /):',
            f'    return self.sigfields.{methname}',
            )))
    del methname

    def _content_repr(self, /):
        dct = self.sigfields
        return ', '.join(map(': '.join, zip(dct, map(repr, dct.values()))))

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.rootrepr
        _pretty.pretty_kwargs(self.sigfields, p, cycle, root)

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(ptolcls, **self.sigfields)


###############################################################################
###############################################################################
