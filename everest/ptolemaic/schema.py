###############################################################################
''''''
###############################################################################


import inspect as _inspect
import collections as _collections
import functools as _functools
import operator as _operator
import weakref as _weakref
import itertools as _itertools

from .eidos import Eidos as _Eidos
from .params import Param as _Param, Signature as _Signature


class Schema(_Eidos):
    '''
    The metaclass of all Schema classes.
    '''

    def _collect_params(cls, /):
        params = dict()
        for name, note in cls.__annotations__.items():
            if note is _Param:
                note = note()
            elif not isinstance(note, _Param):
                continue
            value = (
                cls.__dict__[name] if name in cls.__dict__
                else NotImplemented
                )
            bound = note(name=name, value=value)
            deq = params.setdefault(name, _collections.deque())
            deq.append(bound)
        for base in cls.__bases__:
            if not isinstance(base, Schema):
                continue
            for name, param in base.signature.items():
                deq = params.setdefault(name, _collections.deque())
                deq.append(param)
        return (
            _functools.reduce(_operator.getitem, reversed(deq))
            for deq in params.values()
            )

    def _get_signature(cls, /):
        return _Signature(*cls._collect_params())

    @property
    def signature(cls, /):
        if not '_signature' in cls.__dict__:
            cls._signature = cls._get_signature()
        return cls._signature

    @property
    def __signature__(cls, /):
        return cls.signature.signature.replace(return_annotation=cls)

    def _ptolemaic_concrete_namespace__(cls, /):
        return {
            **super()._ptolemaic_concrete_namespace__(),
            **cls.signature,
            }

    def __class_init__(cls, /):
        super().__class_init__()
        cls.premade = _weakref.WeakValueDictionary()

    def parameterise(cls, /, *args, **kwargs):
        return cls.signature(*args, **kwargs)

    def construct(cls, *args, **kwargs):
        params = cls.parameterise(*args, **kwargs)
        premade, paramid = cls.premade, params.hashcode
        if paramid in premade:
            return premade[paramid]
        obj = premade[paramid] = cls.create_object(params=params)
        obj.__init__()
        return obj


###############################################################################
###############################################################################
