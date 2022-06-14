###############################################################################
''''''
###############################################################################


import inspect as _inspect

from everest import ur as _ur

from .comp import Comps as _Comps, Comp as _Comp


_pempty = _inspect._empty


class Organs(_Comps):

    ...


class Organ(_Comp):

    __merge_fintyp__ = Organs
    _slotcached_ = True

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.ligatures = _ur.DatDict(params.ligatures)
        if params.hint is _pempty:
            params.hint = params.arg
        return params

    def __bound_get__(self, instance, name, /):
        typ = self.arg
        params = typ.Params(**dict(self._yield_arguments(
            instance, _inspect.signature(typ)
            )))
        return typ.construct(params, _corpus_=(instance, name))


###############################################################################
###############################################################################
