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

    @_abc.abstractmethod
    def __bound_owner_get__(self, owner: type, name: str, /):
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

    __slots__ = ('name', 'obj')

    def __init__(self, obj: BindableObject, /):
        self.obj = obj

    def __set_name__(self, owner, name, /):
        if hasattr(self, 'name'):
            raise RuntimeError("Cannot reset name on BoundObject.")
        self.name = name

    def __get__(self, instance, owner, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("BoundObject has not had its name set.")
        if instance is None:
            return self.obj.__bound_owner_get__(owner, name)
        return self.obj.__bound_get__(instance, name)

    def __set__(self, instance, value, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("BoundObject has not had its name set.")
        return self.obj.__bound_set__(instance, name, value)

    def __delete__(self, instance, value, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("BoundObject has not had its name set.")
        return self.obj.__bound_delete__(instance, name)


###############################################################################
###############################################################################
