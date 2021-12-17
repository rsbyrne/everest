###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator

from everest.utilities import caching as _caching

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.params import (
    Sig as _Sig, Param as _Param, ParamProp as _ParamProp
    )


def collect_params(cls, /):
    params = dict()
    for name, note in cls.__annotations__.items():
        deq = params.setdefault(name, _collections.deque())
        if note is _Param:
            param = note()
        elif isinstance(note, _Param):
            param = note
        else:
            param = _Param(note)
        deq.append(param)
    for base in cls.__bases__:
        if not isinstance(base, Schema):
            continue
        for name, param in base.sig.params.items():
            deq = params.setdefault(name, _collections.deque())
            deq.append(param)
    out = {}
    for name, deq in params.items():
        if len(deq) == 1:
            param = deq[0]
        else:
            param = _functools.reduce(_operator.getitem, reversed(deq))
        if hasattr(cls, name):
            if (value := getattr(cls, name)) != param.value:
                param = param(value=value)
        out[name] = param
    return out


class Schema(_Ousia):
    '''
    The metaclass of all Schema classes.
    '''

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        conc = cls.Concrete
        with conc.clsmutable:
            for name in cls.sig.params:
                setattr(conc, name, _ParamProp(name))

    def get_signature(cls, /):
        return _Sig(**collect_params(cls))


class SchemaBase(metaclass=Schema):

    @classmethod
    def instantiate(cls, params, /):
        obj = cls.create_object()
        obj.params = params
        obj.__init__()
        return obj


###############################################################################
###############################################################################


# class MyClass(metaclass=Schema):
#     a: Param.Pos[int]
#     b: Param.Pos[float] = 2.
#     c: int = 3
#     args: Param.Args
#     d: Param.Kw[int]
#     kwargs: Param.Kwargs
