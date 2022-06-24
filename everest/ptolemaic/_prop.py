###############################################################################
''''''
###############################################################################


import inspect as _inspect

from .smartattr import SmartAttr as _SmartAttr
from .content import Kwargs as _Kwargs


class Props(_Kwargs):

    ...


class Prop(_SmartAttr):

    __merge_fintyp__ = Comps

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        if params.hint is NotImplemented:
            params.hint = _inspect.signature(params.arg).return_annotation
        return params

    def __bound_get__(self, instance, name, /):
        return self.arg(instance)


###############################################################################
###############################################################################
