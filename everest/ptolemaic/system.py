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
from .prop import Prop as _Prop
from .organ import Organ as _Organ
from .field import Field as _Field


def _field_bodycall(body, arg=None, /, **kwargs):
    out = _Field._field_bodycall(body, arg, **kwargs)
    if arg is not None:
        return Prop.__body_call__(arg)


class System(_Tekton, _Ousia):

    ### Descriptor behaviours for class and instance:

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield _Organ
        yield _Prop

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
