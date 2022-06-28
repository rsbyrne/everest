###############################################################################
''''''
###############################################################################


from functools import partial as _partial
import types as _types
import inspect as _inspect

from everest.utilities import pretty as _pretty

from . import ptolemaic as _ptolemaic
from .tekton import Tekton as _Tekton
from .ousia import Ousia as _Ousia
from .utilities import get_ligatures as _get_ligatures
from .smartattr import SmartAttr as _SmartAttr


def ligated_function(name, instance, /):
    func = getattr(instance.__ptolemaic_class__, name).__get__(instance)
    bound = _get_ligatures(func, instance)
    return func(*bound.args, **bound.kwargs)


class Ligation(_SmartAttr):
    ...
#     bindings: dict
#     kwargs: dict

#     @classmethod
#     def parameterise(cls, /, *args, **kwargs):
#         params = super().parameterise(*args, **kwargs)
#         return params

#     @classmethod
#     def adjust_params_for_content(cls, params, content, /):
#         super().adjust_params_for_content(params, content)
#         sig = _inspect.signature(content)
        


class Organ(Ligation):
    ...
    # def _get_getter_(self, obj, name, /):
    #     if isinstance(o)


class Prop(Ligation):

    # @classmethod
    # def parameterise(cls, /, *args, **kwargs):
    #     params = super().parameterise(*args, **kwargs)
    #     if params.hint is None:
    #         content = params.content
    #         if isinstance(content, _ptolemaic.Kind):
    #             params.hint = content
    #         elif isinstance(content, _types.FunctionType):
    #             params.hint = content.__annotations__.get('return', None)
    #     return params

    def _get_getter_(self, obj, name, /):
        if isinstance(obj, _types.FunctionType):
            return _partial(ligated_function, name)
        return super()._get_getter_(kls, name)


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

    __slots__ = ('params',)

    ### Descriptor-like behaviours:

    @classmethod
    def __field_get__(cls, name, instance, /):
        return instance.params[cls._field_indexer(name)]

    @classmethod
    def __prop_get__(cls, name, instance, /):
        return cls[
            tuple(_get_ligatures(cls, instance).arguments.values())
            ]

    @classmethod
    def __organ_get__(cls, name, instance, /):
        out = cls.instantiate(
            tuple(_get_ligatures(cls, instance).arguments.values())
            )
        out.__set_name__(instance, name)
        return out

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

    def make_epitaph(self, /):
        cls = self.__ptolemaic_class__
        return cls.taphonomy.getitem_epitaph(cls, tuple(self.params))


###############################################################################
###############################################################################
