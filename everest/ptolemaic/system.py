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
        body[name] = body['comp'](func)


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
            for key, val in self.params.items()
            )

    def _pretty_repr_(self, p, cycle, root=None):
        bound = self.__ptolemaic_class__.__signature__.bind_partial()
        bound.arguments.update(self.params)
        if root is None:
            root = self.rootrepr
        _pretty.pretty_argskwargs(
            (bound.args, bound.kwargs), p, cycle, root=root
            )


###############################################################################
###############################################################################
