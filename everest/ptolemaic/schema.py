###############################################################################
''''''
###############################################################################


import inspect as _inspect
import collections as _collections
import functools as _functools
import operator as _operator

from .eidos import Eidos as _Eidos
from . import params as _params


class Schema(_Eidos):
    '''
    The metaclass of all Schema classes.
    '''

    _req_slots__ = ('params',)

    def _process_params(cls, /):
        annotations = dict()
        for mcls in reversed(cls.__mro__):
            if '__annotations__' not in mcls.__dict__:
                continue
            for name, annotation in mcls.__annotations__.items():
                if annotation is _params.Param:
                    annotation = _params.Param()
                elif not isinstance(annotation, _params.Param):
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

    def _ptolemaic_signature__(cls, /):
        classparams = cls.classparams = {
            pm.name: pm for pm in cls._process_params()
            }
        cls.Params = _params.Params[cls]
        return _inspect.Signature(
            pm.parameter for pm in classparams.values()
            )

    def _ptolemaic_concrete_namespace__(cls, /):
        return super()._ptolemaic_concrete_namespace__() | cls.classparams

    def parameterise(cls, /, *args, **kwargs):
        return args, kwargs

    def instantiate(cls, params, /:
        obj = super().instantiate(params)
        obj.params = params
        obj.__init__()
        return obj

    def construct(cls, *args, **kwargs):
        params = cls.Params(*args, **kwargs)
        return cls.instantiate(params)

#     @classmethod
#     def _add_subclasses(cls, /):
#         pass


###############################################################################
###############################################################################
