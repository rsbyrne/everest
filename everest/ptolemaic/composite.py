###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest.utilities import pretty as _pretty

from .ousia import Ousia as _Ousia
from .pentheros import Pentheros as _Pentheros


class Composite(_Pentheros, _Ousia):
    ...


class CompositeBase(metaclass=Composite):

    __req_slots__ = ('params',)

    @classmethod
    def construct(cls, params: _collabc.Sequence, /):
        return super().construct(params=params, **params._asdict())

    def remake(self, /, **kwargs):
        return self.__ptolemaic_class__.instantiate(
            tuple({**self.params._asdict(), **kwargs}.values())
            )

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        if cls.arity == 1:
            arg = (arg,)
        return cls.instantiate(arg)

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}" for key, val in self.params.items()
            )

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def _repr_pretty_(self, p, cycle, root=None):
        bound = self.__signature__.bind_partial()
        bound.arguments.update(self.params._asdict())
        if root is None:
            root = self.rootrepr
        _pretty.pretty_argskwargs(
            (bound.args, bound.kwargs), p, cycle, root=root
            )

    def make_epitaph(self, /):
        ptolcls = self.__ptolemaic_class__
        params = self.params
        if ptolcls.arity == 1:
            params = params[0]
        return ptolcls.taphonomy.getitem_epitaph(ptolcls, params)


###############################################################################
###############################################################################
