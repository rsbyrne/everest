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


class Comps(_Kwargs):

    ...


class Comp(_SmartAttr):

    ligatures: _collabc.Mapping = _ur.DatDict()

    __merge_fintyp__ = Comps

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.ligatures = _ur.DatDict(params.ligatures)
        return params

    @classmethod
    def __body_call__(cls, body, arg=None, /, **ligatures):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **ligatures)
        return cls(
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
        func = self.arg
        sig = _inspect.signature(func)
        bound = sig.bind_partial()
        bound.arguments.update(self._yield_arguments(instance, sig))
        return func(*bound.args, **bound.kwargs)

    def __directive_call__(self, body, name, /):
        super().__directive_call__(body, name)
        # if name in body['__req_slots__']:


###############################################################################
###############################################################################
