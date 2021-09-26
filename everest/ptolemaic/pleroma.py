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


def gather_slots(bases, /):
    return set(_itertools.chain.from_iterable(
        base.reqslots for base in bases if hasattr(base, 'reqslots')
        ))


class Pleroma(_ABCMeta):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    Param = _params.Param
    _concrete = False

    reqslots = ('_softcache', 'params', '__weakref__')

    def _process_reqslots(cls, /):
        meta = type(cls)
        reqslots = set()
        reqslots.update(gather_slots((meta, *meta.__bases__)))
        reqslots.update(gather_slots(cls.__bases__))
        if 'reqslots' in cls.__dict__:
            reqslots.update(set(cls.reqslots))
        return tuple(sorted(reqslots))

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
        cls.reqslots = cls._process_reqslots()
        params = cls._process_params()
        cls._paramsdict = {pm.name: pm for pm in params}
        cls.__signature__ = _inspect.Signature(pm.parameter for pm in params)
        cls.Params = _params.Params[cls]
        cls.Concrete = Concrete(cls)
        cls._cls_extra_init_()

    def _cls_extra_init_(cls, /):
        pass

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

    def __getitem__(cls, arg, /):
        if isinstance(arg, cls.Params):
            return cls.instantiate(arg)
        raise TypeError(type(arg))


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
        pass

    @classmethod
    def check_param(cls, arg, /):
        return True

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bad = tuple(_itertools.filterfalse(
            cls.check_param,
            _itertools.chain(args, kwargs.values())
            ))
        if bad:
            raise RuntimeError(f"Bad parameterisation of {cls}: {bad}.")
        return type(cls).parameterise(cls, *args, **kwargs)

    @classmethod
    def instantiate(cls, params, /, *args, **kwargs):
        return type(cls).instantiate(cls, params, *args, **kwargs)

    @classmethod
    def construct(cls, /, *args, **kwargs):
        return type(cls).construct(cls, *args, **kwargs)

    def __init__(self, /):
        pass

    def _repr(self, /):
        return self.params.__str__()

    @_utilities.caching.soft_cache(None)
    def __repr__(self, /):
        return f"{type(self).basecls.__qualname__}({self._repr()})"


###############################################################################
###############################################################################
