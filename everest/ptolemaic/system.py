###############################################################################
''''''
###############################################################################


from functools import partial as _partial

from everest.utilities import pretty as _pretty
from everest import ur as _ur

from .tekton import Tekton as _Tekton
from .ousia import Ousia as _Ousia
from .prop import Prop as _Prop


def _organ_bodymeth_(*args, _attrkwargs_=_ur.DatDict(), **kwargs):
    return _Prop.__body_call__(
        *args,
        _attrkwargs_={**_attrkwargs_, 'asorgan': True},
        **kwargs
        )


class System(_Tekton, _Ousia):

    ### Descriptor behaviours for class and instance:

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield _Prop

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'organ', _partial(_organ_bodymeth_, body)

    @classmethod
    def process_shadow(meta, body, name, val, /):
        exec('\n'.join((
            f"def {name}({', '.join((sh.name for sh in val.shades))}):",
            f"    return {val.evalstr}",
            )))
        func = staticmethod(eval(name))
        func.__module__ = body['__module__']
        func.__qualname__ = body['__qualname__'] + '.' + name
        body[name] = body['prop'](func)


class _SystemBase_(metaclass=System):

    ### Class setup:

    @classmethod
    def _get_returnanno(cls, /):
        return cls

    ### Representations:

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}"
            for key, val in self.params.items()
            )

    def _pretty_repr_(self, p, cycle, root=None):
        bound = self.__ptolemaic_class__.__signature__.bind_partial()
        bound.arguments.update(self.params)
        args = tuple(arg for arg in bound.args if arg is not NotImplemented)
        kwargs = {
            key: val
            for key, val in bound.kwargs.items()
            if val is not NotImplemented
            }
        if root is None:
            root = self.__ptolemaic_class__
        _pretty.pretty_argskwargs(
            (args, kwargs), p, cycle, root=root
            )


###############################################################################
###############################################################################
