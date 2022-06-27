###############################################################################
''''''
###############################################################################


from . import ptolemaic as _ptolemaic
from .ousia import Ousia as _Ousia
from .eidos import Eidos as _Eidos, SmartAttr as _SmartAttr
from .utilities import get_ligatures as _get_ligatures


class Organ(_SmartAttr):

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        content = params.content
        if not isinstance(content, _ptolemaic.Kind):
            raise ValueError(content)
        if params.hint is None:
            params.hint = content
        return params


def ligated_function(instance, name, /):
    func = getattr(instance.__ptolemaic_class__, name).__get__(instance)
    bound = _get_ligatures(func, instance)
    return func(*bound.args, **bound.kwargs)


class Prop(_SmartAttr):

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        if params.hint is None:
            content = params.content
            if isinstance(content, _ptolemaic.Kind):
                params.hint = content
            elif isinstance(content, _types.FunctionType):
                params.hint = content.__annotations__.get('return', None)
        return params

    @classmethod
    def _get_getter_(cls, obj):
        if isinstance(obj, _ptolemaic.Kind):
            return super()._get_getter_(obj)
        if isinstance(obj, _types.FunctionType):
            return ligated_function
        raise TypeError(type(obj))


class System(_Ousia, _Eidos):

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

    @classmethod
    def _yield_slots(cls, /):
        yield from super()._yield_slot_sources()
        for source in (cls.__props__, cls.__organs__):
            yield from source.items()


###############################################################################
###############################################################################
