###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import inspect as _inspect
from collections import abc as _collabc

from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .sprite import Sprite as _Sprite
from .smartattr import (
    SmartAttr as _SmartAttr,
    SmartAttrDirective as _SmartAttrDirective,
    # ContentType as _ContentType
    )
from .shadow import Shade as _Shade
from .pathget import PathGet as _PathGet, PathError as _PathError


class Prop(_SmartAttr):

    bindings: dict
    asorgan: bool = False

    @classmethod
    def _parameterise_(self, /, *args, bindings=None, **kwargs):
        if bindings is None:
            bindings = ((), {})
        elif isinstance(bindings, _collabc.Mapping):
            bindings = ((), bindings)
        elif not isinstance(bindings, _collabc.Sequence):
            raise ValueError
        return super()._parameterise_(*args, bindings=bindings, **kwargs)

    @classmethod
    def _get_bindings(cls, content, bndargs, bndkwargs, /):
        if isinstance(content, _ptolemaic.Ideal):
            return content.parameterise(*bndargs, **bndkwargs)
        if callable(content):
            signature = _inspect.signature(content)
            bound = signature.bind_partial(*bndargs, **bndkwargs)
            return bound.arguments
        if bndargs:
            raise ValueError
        return bndkwargs

    @classmethod
    def adjust_params_for_content(cls, params, content, /):
        super().adjust_params_for_content(params, content)
        params.bindings = cls._get_bindings(content, *params.bindings)

    def _prop_getter(self, name, obj, /):
        content = obj.__mro_getattr__(name)
        asorgan = self.asorgan
        bindings = self.bindings
        if isinstance(content, _ptolemaic.Kind):
            if asorgan:
                out = content._instantiate_(bindings)
                obj._register_innerobj(name, out)
                return out
            return content[bindings]
        elif callable(content):
            content = content.__get__(obj)
            signature = _inspect.signature(content)
            bound = signature.bind_partial()
            bound.apply_defaults()
            bound.arguments.update(self.bindings)
            return content(*bound.args, **bound.kwargs)
        elif isinstance(content, str):
            return eval(content, {'self': obj}, self.bindings)
        raise RuntimeError

    def _get_getter_(self, obj, name, /):
        return _partial(self._prop_getter, name)


###############################################################################
###############################################################################


    # @classmethod
    # def __body_call__(
    #         cls, body, content=None, /, *, _attrkwargs_=_ur.DatDict(), **kwargs
    #         ):
    #     if content is None:
    #         return _partial(
    #             cls.__body_call__, body, _attrkwargs_=_attrkwargs_, **kwargs
    #             )
    #     bindings = {}
    #     for key, val in kwargs.items():
    #         if isinstance(val, _Shade):
    #             if val.prefix is not None:
    #                 raise NotImplementedError
    #             val = _PathGet(f".{val.name}")
    #         bindings[key] = val
    #     return _SmartAttrDirective(
    #         cls, {'bindings': bindings, **_attrkwargs_}, content
    #         )

    # @classmethod
    # def adjust_params_for_content_signature(cls, params, sig, contenttype):
    #     super().adjust_params_for_content_signature(params, sig, contenttype)
    #     if contenttype in \
    #             (_ContentType.STATICLIKE, _ContentType.CLASSLIKE):
    #         bindings = params.bindings = dict(params.bindings)
    #         for nm, pm in sig.parameters.items():
    #             if nm not in bindings:
    #                 if pm.default is sig.empty:
    #                     if pm.kind not in (2, 4):
    #                         bindings[nm] = _PathGet('.'+nm)
