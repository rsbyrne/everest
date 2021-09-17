###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import weakref as _weakref
import itertools as _itertools
import inspect as _inspect

from . import _utilities

_Param = _utilities.params.Param
_Bind = _utilities.params.Bind


def yield_classbody_params(cls):
    for name, annotation in cls.__annotations__.items():
        if not isinstance(annotation, _Param):
            continue
        if hasattr(cls, name):
            yield annotation(name, getattr(cls, name))
        else:
            yield annotation(name)


def get_classbody_signature(cls):
    return _inspect.Signature(yield_classbody_params(cls))


class PtolemaicMeta(_ABCMeta):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    __annotations__ = dict()

    Param = _Param

    def _cls_extra_init_(cls, /):
        pass

    def __new__(meta, *args, clskwargs=None, **kwargs):
        cls = super().__new__(meta, *args, **kwargs)
        if clskwargs is None:
            cls._cls_extra_init_()
        else:
            cls._cls_extra_init_(**clskwargs)
        cls.__signature__ = get_classbody_signature(cls)
        return cls

    def parameterise(cls, bind, /, *args, **kwargs):
        bind(*args, **kwargs)

    def instantiate(cls, params):
        obj = object.__new__(cls)
        obj._softcache = dict()
        obj.params = params
        obj.__init__()
        return obj

    @classmethod
    def param_checker(cls, arg):
        return True

    def construct(cls, *args, **kwargs):
        bind = _Bind(cls.param_checker)
        cls.parameterise(bind, *args, **kwargs)
        return cls.instantiate(bind.get_params(cls.__signature__))

    @property
    def __call__(cls):
        return cls.construct


###############################################################################
###############################################################################
