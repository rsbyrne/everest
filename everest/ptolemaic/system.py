###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import types as _types
import inspect as _inspect
import itertools as _itertools

from everest.utilities import pretty as _pretty

from . import ptolemaic as _ptolemaic
from .tekton import Tekton as _Tekton
from .ousia import Ousia as _Ousia
from .smartattr import (
    SmartAttr as _SmartAttr,
    SmartAttrDirective as _SmartAttrDirective,
    )
from .shadow import Shade as _Shade


class Prop(_SmartAttr):

    ligatures: dict
    bindings: dict

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


class Organ(Prop):

    def _kindlike_getter(self, name, obj, /):
        callble = obj.__mro_getattr__(name)
        bound = self._get_callble_bound(name, callble, obj)
        out = callble.__instantiate__(tuple(bound.arguments.values()))
        out.prepare_innerobj(name, obj)
        return out

    def _functionlike_getter(self, name, obj, /):
        out = super()._functionlike_getter(name, obj)
        out.add_innerobj(name, obj)
        return out

    def _get_getter_(self, obj, name, /):
        if isinstance(obj, _ptolemaic.Kind):
            return _partial(self._kindlike_getter, name)
        return super()._get_getter_(obj, name)


class System(_Tekton, _Ousia):

    ### Descriptor behaviours for class and instance:

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield Organ
        yield Prop

    @classmethod
    def process_shadow(meta, body, name, val, /):
        exec('\n'.join((
            f"def {name}(self, {', '.join((sh.name for sh in val.shades))}):",
            f"    return {val.evalstr}",
            )))
        func = eval(name)
        func.__module__ = body['__module__']
        func.__qualname__ = body['__qualname__'] + '.' + name
        body[name] = body['prop'](func)


class _SystemBase_(metaclass=System):

    ### Class setup:

    @classmethod
    def _get_returnanno(cls, /):
        return cls

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._field_indexer = tuple(cls.__fields__).index

    ### Representations:

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}"
            for key, val in zip(self.__fields__, self.params)
            )

    def _repr_pretty_(self, p, cycle, root=None):
        bound = self.__signature__.bind_partial()
        bound.arguments.update(zip(self.__fields__, self.params))
        if root is None:
            root = self.rootrepr
        _pretty.pretty_argskwargs(
            (bound.args, bound.kwargs), p, cycle, root=root
            )


###############################################################################
###############################################################################
