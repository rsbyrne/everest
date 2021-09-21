###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import weakref as _weakref
import itertools as _itertools
import inspect as _inspect

from . import _utilities
from . import params as _params

_classtools = _utilities.classtools

_Param = _params.Param
_Binder = _params.Binder
_Params = _params.Params


class Pleroma(_ABCMeta):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    Param = _Param

    reqslots = ('_softcache', 'params', '__weakref__')

    def _cls_extra_init_(cls, /):
        pass

    @staticmethod
    def gather_slots(bases, /):
        return set(_itertools.chain.from_iterable(
            base.reqslots for base in bases if hasattr(base, 'reqslots')
            ))

    @classmethod
    def _add_concrete_(meta, cls, /):
        reqslots = meta.gather_slots((meta, *meta.__bases__))
        reqslots.update(meta.gather_slots(cls.__bases__))
        if 'reqslots' in cls.__dict__:
            reqslots.update(set(cls.reqslots))
        reqslots = cls.reqslots = tuple(reqslots)
        cls.concrete = Concrete(
            f"{cls.__name__}_concrete", (cls,),
            {'__slots__': reqslots, 'basecls': cls}
            )

    def process_classbody_params(cls, /):
        toadd = dict()
        for mcls in cls.__mro__:
            if '__annotations__' not in mcls.__dict__:
                continue
            for name, annotation in mcls.__annotations__.items():
                if not issubclass(annotation, _Param):
                    continue
                if name in toadd:
                    continue
                specname = f'_param_{name}'
                if hasattr(cls, specname):
                    param = getattr(cls, specname)
                elif hasattr(cls, name):
                    att = getattr(cls, name)
                    param = annotation(name, att)
                else:
                    param = annotation(name)
                setattr(cls, name, param)
                toadd[name] = param.parameter
        cls.__signature__ = _inspect.Signature(toadd.values())

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
        cls.process_classbody_params()
        meta._add_concrete_(cls)
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

    @property
    def __call__(cls):
        return cls.concrete.__call__


class Concrete(Pleroma):

    def __new__(meta, name, bases, namespace, /,):
        if len(bases) > 1:
            raise RuntimeError
        cls = super().__new__(meta, name, bases, namespace, _concrete=True)
        base = bases[0]
        cls.__signature__ = base.__signature__
        return cls

    def __call__(cls, *args, **kwargs):
        bind = _Binder()
        cls.parameterise(bind, *args, **kwargs)
        params = _Params(cls.__signature__, *bind.args, **bind.kwargs)
        return cls.instantiate(params)


###############################################################################
###############################################################################
