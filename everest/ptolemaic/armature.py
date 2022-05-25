###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from .tekton import Tekton as _Tekton, SmartAttr as _SmartAttr
from .composite import Composite as _Composite


class Prop(_SmartAttr):

    __params__ = ('func',)
    __defaults__ = tuple(NotImplemented for key in __params__)

    @classmethod
    def process_func(cls, func, /):
        return func

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        try:
            return getattr(instance, self.cachedname)
        except AttributeError:
            try:
                value = self.func(instance)
            except Exception as exc:
                raise RuntimeError from exc
            with instance.mutable:
                setattr(instance, self.cachedname, value)
            return value

    def __set__(self, instance, value, /):
        raise NotImplementedError


class Comp(_SmartAttr):
    ...


class Armature(_Tekton, _Composite):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield Prop
        yield Comp

    @classmethod
    def prop(meta, func: _collabc.Callable, /):
        return meta.Prop(name=func.__name__, func=func)


class ArmatureBase(metaclass=Armature):
    ...


###############################################################################
###############################################################################
