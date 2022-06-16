###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import inspect as _inspect
import functools as _functools

from everest import ur as _ur

from .utilities import BindableObject as _BindableObject
from .smartattr import SmartAttr as _SmartAttr
from .sprite import Sprite as _Sprite
from .content import Kwargs as _Kwargs
from .shadow import Shade as _Shade


_pempty = _inspect._empty


class Organs(_Kwargs):

    ...


class Organ(_SmartAttr):

    ligatures: _collabc.Mapping = _ur.DatDict()

    __merge_fintyp__ = Organs
    _slotcached_ = True

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.ligatures = _ur.DatDict(params.ligatures)
        if params.hint is _pempty:
            params.hint = params.arg
        return params

    @classmethod
    def __body_call__(cls, body, arg=None, /, **ligatures):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **ligatures)
        return cls.__body_construct__(
            body,
            arg=arg,
            hint=_inspect.signature(arg).return_annotation,
            ligatures=ligatures,
            )

    def _yield_arguments(self, instance, signature, /):
        ligatures = self.ligatures
        for nm, pm in signature.parameters.items():
            try:
                val = ligatures[nm]
            except KeyError:
                try:
                    val = getattr(instance, nm)
                except AttributeError:
                    val = pm.default
                    if val is _pempty:
                        raise RuntimeError(f"Missing argument: {nm}")
            else:
                if isinstance(val, _Shade):
                    val = val.__get__(instance)
            yield nm, val

    def __bound_get__(self, instance, name, /):
        typ = self.arg
        params = typ.Params(**dict(self._yield_arguments(
            instance, _inspect.signature(typ)
            )))
        return typ.construct(params, _corpus_=(instance, name))


###############################################################################
###############################################################################
