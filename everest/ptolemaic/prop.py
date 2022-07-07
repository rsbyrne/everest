###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import inspect as _inspect

from .smartattr import (
    SmartAttr as _SmartAttr,
    SmartAttrDirective as _SmartAttrDirective,
    )
from .shadow import Shade as _Shade


class Prop(_SmartAttr):

    ligatures: dict = {}
    bindings: dict = {}

    @classmethod
    def __body_call__(cls, body, arg=None,/, **kwargs):
        if arg is None:
            return _partial(cls.__body_call__, body, **kwargs)
        ligatures, bindings = {}, {}
        for key, val in kwargs.items():
            if isinstance(val, _Shade):
                if val.prefix is not None:
                    raise NotImplementedError
                ligatures[key] = val.name
            else:
                bindings[key] = val
        return _SmartAttrDirective(
            cls, dict(ligatures=ligatures, bindings=bindings), arg
            )

    def _get_callble_bound(self, name, callble, corpus, /):
        signature = _inspect.signature(callble)
        bound = signature.bind_partial()
        bound.apply_defaults()
        arguments = bound.arguments
        ligatures, bindings = self.ligatures, self.bindings
        for key in signature.parameters:
            try:
                arguments[key] = bindings[key]
            except KeyError:
                getkey = ligatures.get(key, key)
                try:
                    arguments[key] = getattr(corpus, getkey)
                except AttributeError:
                    if key not in arguments:
                        raise ValueError(f"Missing key: {key}")
        return bound

    def _functionlike_getter(self, name, obj, /):
        callble = obj.__mro_getattr__(name).__get__(obj)
        bound = self._get_callble_bound(name, callble, obj)
        return callble(*bound.args, **bound.kwargs)

    def _get_getter_(self, obj, name, /):
        return _partial(self._functionlike_getter, name)


###############################################################################
###############################################################################
