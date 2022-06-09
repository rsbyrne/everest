###############################################################################
''''''
###############################################################################


import abc as _abc


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
            raise RuntimeError("Cannot reset name on NameBinding.")
        self.name = name

    def __get__(self, instance, owner, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("NameBinding has not had its name set.")
        if instance is None:
            return self.obj.__bound_owner_get__(owner, name)
        return self.obj.__bound_get__(instance, name)

    def __set__(self, instance, value, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("NameBinding has not had its name set.")
        return self.obj.__bound_set__(instance, name, value)

    def __delete__(self, instance, value, /):
        try:
            name = self.name
        except AttributeError:
            raise RuntimeError("NameBinding has not had its name set.")
        return self.obj.__bound_delete__(instance, name)


from collections import deque as _deque


class Switch:

    __slots__ = ('_state', '_prevstates')

    def __init__(self, state: bool = False, /):
        self._state = state
        self._prevstates = _deque()

    @property
    def state(self, /):
        return self._state

    @state.setter
    def state(self, value, /):
        self._state = value

    def toggle(self, state:bool=None, /):
        if state is None:
            state = not self._state
        self._state = bool(state)

    def __bool__(self, /):
        return self._state

    def __repr__(self, /):
        return f"<{self.__class__.__name__}({self._state})>"

    def __enter__(self, tostate: bool = True, /):
        self._prevstates.append(self._state)
        self.toggle(tostate)

    def __exit__(self, /, *_):
        self.toggle(self._prevstates.pop())

    def __call__(self, state=None, /):
        if state is None:
            state = not self.state
        return SwitchAs(state)


class SwitchAs:

    __slots__ = ('switch', 'state')

    def __init__(self, switch: Switch, state: bool, /):
        self.switch, self.state = switch, state

    def __enter__(self, /):
        self.switch.__enter__(self.state)

    def __exit__(self, /, *_):
        self.switch.__exit__(*_)


class SwitchProperty:

    __slots__ = ('default', 'instances')

    def __init__(self, default: bool = False, /):
        self.default = state
        self.instances = _weakref.WeakKeyDictionary()

    def __get__(self, instance, owner=None, /):
        try:
            return self.instances[instance]
        except AttributeError:
            switch = self.instances[instance] = Switch(self.default)
            return switch

    def __set__(self, instance, value, /):
        self.__get__(instance).toggle(value)


###############################################################################
###############################################################################
