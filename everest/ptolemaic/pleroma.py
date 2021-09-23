###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import weakref as _weakref
import itertools as _itertools
import inspect as _inspect
import collections as _collections
import functools as _functools
import operator as _operator

from . import _utilities
from . import params as _params

_classtools = _utilities.classtools

_Param = _params.Param
_Binder = _params.Binder
_Params = _params.Params


def gather_slots(bases, /):
    return set(_itertools.chain.from_iterable(
        base.reqslots for base in bases if hasattr(base, 'reqslots')
        ))

def sort_params(params, /):
    params = sorted(params, key=(lambda x: x.default is not _inspect._empty))
    params = sorted(params, key=(lambda x: x.kind))
    return params


class Pleroma(_ABCMeta):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    Param = _Param

    reqslots = ('_softcache', 'params', '__weakref__')

    def _combine_reqslots(cls, /):
        meta = type(cls)
        reqslots = set()
        reqslots.update(gather_slots((meta, *meta.__bases__)))
        reqslots.update(gather_slots(cls.__bases__))
        if 'reqslots' in cls.__dict__:
            reqslots.update(set(cls.reqslots))
        cls.reqslots = tuple(sorted(reqslots))

    def _add_concrete(cls, /):
        cls.concrete = Concrete(cls)

    def _process_classbody_params(cls, /):
        annotations = dict()
        for mcls in reversed(cls.__mro__):
            if '__annotations__' not in mcls.__dict__:
                continue
            for name, annotation in mcls.__annotations__.items():
                if not issubclass(annotation, _Param):
                    continue
                if name in annotations:
                    row = annotations[name]
                else:
                    row = annotations[name] = list()
                row.append(annotation)
        params = _collections.deque()
        for name, row in annotations.items():
            annotation = _functools.reduce(_operator.getitem, reversed(row))
            if hasattr(cls, name):
                att = getattr(cls, name)
                param = annotation(name, att)
            else:
                param = annotation(name)
            params.append(param)
        params = sort_params(params)
        cls._paramsdict = {pm.name: pm for pm in params}
        cls.__signature__ = _inspect.Signature(pm.parameter for pm in params)

    def _cls_extra_init_(cls, /):
        cls._combine_reqslots()
        cls._process_classbody_params()
        cls._add_concrete()

    def __new__(meta,
            name, bases, namespace, /, *,
            _concrete=False, **kwargs
            ):
        if any(isinstance(base, Concrete) for base in bases):
            raise TypeError("Cannot subclass a Concrete type.")
        if _concrete:
            return super().__new__(meta, name, bases, namespace, **kwargs)
        namespace['__slots__'] = ()
        cls = super().__new__(meta, name, bases, namespace, **kwargs)
        cls._cls_extra_init_()
        return cls

    def check_param(cls, arg, /):
        return True

    def parameterise(cls, bind, /, *args, **kwargs):
        bind(*args, **kwargs)
        args, kwargs = bind.args, bind.kwargs
        bad = tuple(_itertools.filterfalse(
            cls.check_param, _itertools.chain(args, kwargs.values())
            ))
        if bad:
            raise TypeError(f"Bad inputs: {bad}")

    def instantiate(cls, params):
        obj = object.__new__(cls)
        obj._softcache = dict()
        obj.params = params
        obj.__init__()
        return obj

    def __call__(cls, /, *args, **kwargs):
        return cls.concrete(*args, **kwargs)


class Concrete(Pleroma):

    def __new__(meta, base, /,):
        name = f"{base.__name__}_concrete"
        namespace = dict(
            __slots__=base.reqslots,
            basecls=base,
            ) | base._paramsdict
        bases = (base,)
        cls = super().__new__(meta, name, bases, namespace, _concrete=True)
        cls.__signature__ = base.__signature__
        return cls

    def __call__(cls, /, *args, **kwargs):
        bind = _Binder()
        cls.parameterise(bind, *args, **kwargs)
        params = _Params(cls.__signature__, *bind.args, **bind.kwargs)
        return cls.instantiate(params)


class Pleromatic(metaclass=Pleroma):

    @classmethod
    def _cls_extra_init_(cls, /):
        type(cls)._cls_extra_init_(cls)


###############################################################################
###############################################################################
