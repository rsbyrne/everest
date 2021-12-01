###############################################################################
''''''
###############################################################################


import inspect as _inspect
import collections as _collections
import functools as _functools
import operator as _operator
import weakref as _weakref
import itertools as _itertools

from everest.ptolemaic.ousia import Ousia as _Ousia
from .params import Param as _Param, Signature as _Signature


class Schema(_Ousia):
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

    @property
    def signature(cls, /):
        if not '_signature' in cls.__dict__:
            cls._signature = cls._get_signature()
        return cls._signature

    @property
    def __signature__(cls, /):
        return cls.signature.signature.replace(return_annotation=cls)

#     def __new__(meta, name, bases, namespace, /):
#         cls = super().__new__(meta, name, bases, namespace)
#         return cls

    def _ptolemaic_concrete_namespace__(cls, /):
        return {
            **super()._ptolemaic_concrete_namespace__(),
            **cls.signature,
            }

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.premade = _weakref.WeakValueDictionary()


class SchemaBase(metaclass=Schema):

    __slots__ = ()

    def get_signature(cls, /):
        return _Signature(*cls._collect_params())

    def construct(cls, *args, **kwargs):
        registrar = cls.Registrar()
        cls.parameterise(registrar, *args, **kwargs)
        params = cls.signature(*registrar.args, **registrar.kwargs)
        premade, paramid = cls.premade, params.hashcode
        if paramid in premade:
            return premade[paramid]
        obj = premade[paramid] = cls.create_object(params=params)
        obj.__init__()
        return obj


###############################################################################
###############################################################################


# from collections import abc as _collabc

# from .system import System as _System

# from .primitive import Primitive as _Primitive
# from . import shades as _shades
# # from .shade import Shade as _Shade


# # class Var(_Ptolemaic):
# #     ...


# class Dat(_shades.Singleton):
# # class Dat(_Shade):

#     isdat = True

#     superclass = None

#     @classmethod
#     def _cls_repr(cls, /):
#         return f"{repr(cls.superclass)}.{super()._cls_repr()}"


# class Schema(_System):

#     _ptolemaic_fixedsubclasses__ = ('Mapp', 'Brace', 'Slyce')

#     Mapp = _shades.DictLike
#     Brace = _shades.TupleLike
#     Slyce = _shades.SliceLike

#     _ptolemaic_subclasses__ = ('Dat',)

#     Dat = Dat

#     isdat = False

#     @classmethod
#     def yield_checktypes(cls, /):
#         yield from super().yield_checktypes()
#         yield _collabc.Mapping, lambda x: cls.Mapp(x)
#         yield _collabc.Sequence, lambda x: cls.Brace(x)
#         yield slice, lambda x: cls.Slyce(x)

#     @classmethod
#     def instantiate(cls, params, /, *args, **kwargs):
#         if all(
#                 isinstance(param, (Dat, _Primitive, tuple, dict))
#                 for param in params.values()
#                 ):
#             return cls.Dat.instantiate(params, *args, **kwargs)
#         return super().instantiate(params, *args, **kwargs)