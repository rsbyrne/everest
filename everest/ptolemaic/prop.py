###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import inspect as _inspect

from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .smartattr import (
    SmartAttr as _SmartAttr,
    SmartAttrDirective as _SmartAttrDirective,
    ContentType as _ContentType
    )
from .shadow import Shade as _Shade
from .pathget import PathGet as _PathGet


class Prop(_SmartAttr):

    bindings: dict
    asorgan: bool = False

    @classmethod
    def __body_call__(
            cls, body, content=None, /, *, _attrkwargs_=_ur.DatDict(), **kwargs
            ):
        if content is None:
            return _partial(
                cls.__body_call__, body, _attrkwargs_=_attrkwargs_, **kwargs
                )
        bindings = {}
        for key, val in kwargs.items():
            if isinstance(val, _Shade):
                if val.prefix is not None:
                    raise NotImplementedError
                val = _PathGet(f".{val.name}")
            bindings[key] = val
        return _SmartAttrDirective(
            cls, {'bindings': bindings, **_attrkwargs_}, content
            )

    @classmethod
    def _parameterise_(self, /, *args, bindings=None, **kwargs):
        if bindings is None:
            bindings = {}
        return super()._parameterise_(*args, bindings=bindings, **kwargs)

    @classmethod
    def adjust_params_for_content_signature(cls, params, sig, contenttype):
        super().adjust_params_for_content_signature(params, sig, contenttype)
        if contenttype in \
                (_ContentType.STATICLIKE, _ContentType.CLASSLIKE):
            bindings = params.bindings = dict(params.bindings)
            for nm, pm in sig.parameters.items():
                if nm not in bindings:
                    if pm.default is sig.empty:
                        bindings[nm] = _PathGet('.'+nm)

    def _get_callble_bound(self, name, callble, corpus, /):
        signature = _inspect.signature(callble)
        bound = signature.bind_partial()
        bound.apply_defaults()
        arguments = bound.arguments
        bindings = self.bindings
        for key in signature.parameters:
            try:
                val = bindings[key]
            except KeyError:
                pass
            else:
                if isinstance(val, _PathGet):
                    val = val(corpus)
                arguments[key] = val
        return bound

    def _callble_getter(self, name, obj, /):
        callble = obj.__mro_getattr__(name).__get__(obj)
        bound = self._get_callble_bound(name, callble, obj)
        asorgan = self.asorgan
        if isinstance(callble, _ptolemaic.Kind):
            if asorgan:
                callble = callble.__class_alt_call__
        out = callble(*bound.args, **bound.kwargs)
        if asorgan:
            obj._register_innerobj(name, out)
        return out

    def _get_getter_(self, obj, name, /):
        return _partial(self._callble_getter, name)


###############################################################################
###############################################################################
