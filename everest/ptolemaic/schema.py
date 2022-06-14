###############################################################################
''''''
###############################################################################


from everest.utilities import pretty as _pretty

from .tekton import Tekton as _Tekton
from .eidos import Eidos as _Eidos
from . import organ as _organ


class Schema(_Tekton, _Eidos):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield _organ.Organ


class _SchemaBase_(metaclass=Schema):

    __slots__ = ('_params',)

    @property
    def params(self, /):
        return self._params

    @params.setter
    def params(self, value, /):
        self._params = self.__ptolemaic_class__.Params(*value)

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
