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


class Pleroma(_ABCMeta):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    Param = _params.Param
    _concrete = False

    mergenames = ('reqslots',)

    reqslots = ('_softcache', 'params', '__weakref__')

    @staticmethod
    def gather_names(bases, name, /):
        return set(_itertools.chain.from_iterable(
            getattr(base, name) for base in bases if hasattr(base, name)
            ))

    def merge_names(cls, name, /):
        meta = type(cls)
        merged = set()
        merged.update(cls.gather_names((meta, *meta.__bases__), name))
        merged.update(cls.gather_names(cls.__bases__, name))
        if name in cls.__dict__:
            merged.update(set(getattr(cls, name)))
        setattr(cls, name, tuple(sorted(merged)))

    def merge_names_all(cls, overname='mergenames'):
        cls.merge_names(overname)
        for name in getattr(cls, overname):
            cls.merge_names(name)

    def _process_params(cls, /):
        annotations = dict()
        for mcls in reversed(cls.__mro__):
            if '__annotations__' not in mcls.__dict__:
                continue
            for name, annotation in mcls.__annotations__.items():
                if not isinstance(annotation, _params.ParamMeta):
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
        return _params.sort_params(params)

    @classmethod
    def __prepare__(meta, name, bases, /):
        return dict()

    def __new__(meta, name, bases, namespace, /, *, _concrete=False):
        if any(isinstance(base, Concrete) for base in bases):
            raise TypeError("Cannot subclass a Concrete type.")
        if _concrete:
            return super().__new__(meta, name, bases, namespace)
        namespace['__slots__'] = ()
        return super().__new__(meta, name, bases, namespace)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls._concrete:
            return
        cls.merge_names_all()
        params = cls._process_params()
        cls._paramsdict = {pm.name: pm for pm in params}
        cls.__signature__ = _inspect.Signature(pm.parameter for pm in params)
        cls.Params = _params.Params[cls]
        cls.Concrete = Concrete(cls)
        cls._cls_extra_init_()

    def _cls_extra_init_(cls, /):
        for name in dir(cls):
            if name.startswith('_cls_') and name.endswith('_init_'):
                if name != '_cls_extra_init_':
                    getattr(cls, name)()

    def parameterise(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    def instantiate(cls, params, /, *args, **kwargs):
        obj = object.__new__(cls.Concrete)
        obj._softcache = dict()
        obj.params = params
        obj.__init__(*args, **kwargs)
        return obj

    def construct(cls, *pa, args=(), kwargs=_utilities.FrozenMap(), **pk):
        return cls.instantiate(cls.Params(*pa, **pk), *args, **kwargs)

    def __call__(cls, /, *args, **kwargs):
        return cls.construct(*args, **kwargs)

    def __class_getitem__(cls, arg, /):
        if isinstance(arg, cls.Params):
            return cls.instantiate(arg)
        raise TypeError(type(arg))

    def __getitem__(cls, arg, /):
        return cls.__class_getitem__(arg)


class Concrete(Pleroma):

    def __new__(meta, base, /,):
        name = f"{base.__qualname__}.Concrete"
        namespace = dict(
            __slots__=base.reqslots,
            basecls=base,
            _concrete=True,
            ) | base._paramsdict
        bases = (base,)
        return super().__new__(meta, name, bases, namespace, _concrete=True)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__signature__ = cls.basecls.__signature__

    def __call__(cls, /, *args, **kwargs):
        raise TypeError("Cannot directly call a Concrete class.")


class Pleromatic(metaclass=Pleroma):

    @classmethod
    def _cls_extra_init_(cls, /):
        type(cls)._cls_extra_init_(cls)

    @classmethod
    def check_param(cls, arg, /):
        return arg

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return type(cls).parameterise(cls,
            *map(cls.check_param, args),
            **dict(zip(kwargs, map(cls.check_param, kwargs.values()))),
            )

    @classmethod
    def instantiate(cls, params, /, *args, **kwargs):
        return type(cls).instantiate(cls, params, *args, **kwargs)

    @classmethod
    def construct(cls, /, *args, **kwargs):
        return type(cls).construct(cls, *args, **kwargs)

    @classmethod
    def __class_getitem__(cls, arg, /):
        return type(cls).__class_getitem__(cls, arg)


###############################################################################
###############################################################################
