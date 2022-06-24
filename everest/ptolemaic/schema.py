###############################################################################
''''''
###############################################################################


from everest.utilities import pretty as _pretty

from .tekton import Tekton as _Tekton
from .eidos import Eidos as _Eidos
from .organ import Organ as _Organ
from .comp import Comp as _Comp


# class _DissolvableWrapper:

#     __slots__ = ('content',)

#     def __init__(self, content, /):
#         self.content = content

#     def __set_name__(cls, owner, name, /):
#         content = self.content
#         content.__module__ = owner.__module__
#         content.__qualname__ = owner.__qualname__ + '.' + name
#         setattr(owner, name)


class Schema(_Tekton, _Eidos):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield _Organ
        yield _Comp

    @classmethod
    def process_shadow(meta, body, name, val, /):
        exec('\n'.join((
            f"def {name}(self, {', '.join((sh.name for sh in val.shades))}):",
            f"    return {val.evalstr}",
            )))
        func = eval(name)
        func.__module__ = body['__module__']
        func.__qualname__ = body['__qualname__'] + '.' + name
        body[name] = func


class _SchemaBase_(metaclass=Schema):

    __slots__ = ('_params',)

    @classmethod
    def _yield_getters(cls, /):
        yield from super()._yield_getters()
        for typ in cls._smartattrtypes:
            for nm, sm in getattr(cls, typ.__merge_name__).items():
                yield nm, sm.__get__

    @property
    def params(self, /):
        return self._params

    @params.setter
    def params(self, value, /):
        self._params = self.__ptolemaic_class__._Params(*value)

    def remake(self, /, **kwargs):
        return self.__ptolemaic_class__.retrieve(
            tuple({**self.params._asdict(), **kwargs}.values())
            )

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}"
            for key, val in self.params._asdict().items()
            )

    def _repr_pretty_(self, p, cycle, root=None):
        bound = self.__signature__.bind_partial()
        bound.arguments.update(self.params._asdict())
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
