###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.switch import *  # Need to update Pleroma to remove need for this


class BindableObject(metaclass=_abc.ABCMeta):

    __slots__ = ()

    @_abc.abstractmethod
    def __bound_get__(self, instance: object, name: str, /):
        raise NotImplementedError

    def __bound_set__(self, instance, name, value, /):
        raise AttributeError(
            f"Can't set attribute: {instance}, {name}"
            )

    def __bound_delete__(self, instance, name, /):
        raise AttributeError(
            f"Can't delete attribute: {instance}, {name}"
            )


class BoundObject:

    __slots__ = ('obj', 'name', 'methprefix')

    def __init__(
            self,
            obj: BindableObject, name: str = None, /, methprefix='bound'
            ):
        self.obj, self.name, self.methprefix = obj, name, methprefix

    def __set_name__(self, owner, name, /):
        if self.name is not None:
            raise RuntimeError("Cannot reset name on BoundObject.")
        self.name = name

    def __get__(self, instance, owner, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("BoundObject has not had its name set.")
        if instance is None:
            return self.obj
        try:
            meth = getattr(self.obj, f"__{self.methprefix}_get__")
        except AttributeError as exc:
            raise TypeError from exc
        return meth(instance, name)

    def __set__(self, instance, value, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("BoundObject has not had its name set.")
        return (
            getattr(self.obj, f"__{self.methprefix}_set__")
            (instance, name, value)
            )

    def __delete__(self, instance, value, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("BoundObject has not had its name set.")
        return (
            getattr(self.obj, f"__{self.methprefix}_delete__")
            (instance, name, value)
            )


###############################################################################
###############################################################################
