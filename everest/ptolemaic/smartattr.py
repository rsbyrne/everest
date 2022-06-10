###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect

from everest import ur as _ur

from .classbody import Directive as _Directive
from .sprite import Sprite as _Sprite
from .utilities import (
    BindableObject as _BindableObject,
    BoundObject as _BoundObject,
    )


_pempty = _inspect._empty


_passthru = lambda x: x


class Getter(metaclass=_Sprite):

    @_abc.abstractmethod
    def __call__(self, instance, owner, /):
        raise NotImplementedError


class OwnerGet(Getter):

    name: str
    default: object

    def __call__(self, instance, owner, /):
        name, default = self.name, self.default
        if default is NotImplemented:
            return getattr(owner, name)
        return getattr(owner, name, default)


class InstanceGet(Getter):

    name: str
    default: object

    def __call__(self, instance, owner, /):
        name, default = self.name, self.default
        if default is NotImplemented:
            return getattr(instance, name)
        return getattr(instance, name, default)


@_Directive.register
@_BindableObject.register
class SmartAttr(metaclass=_Sprite):

    __slots__ = ('cachedname', 'degenerate')

    hint: (type, str, tuple)
    note: str

    __merge_dyntyp__ = dict
    __merge_fintyp__ = _ur.DatDict

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.__merge_name__ = f"__{cls.__name__.lower()}s__"

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        params.__dict__.update(
            (name, getattr(cls, f"process_{name}", _passthru)(val))
            for name, val in params.__dict__.items()
            )
        return params

    @classmethod
    def convert(cls, arg, /):
        if isinstance(arg, cls):
            return arg
        raise TypeError(type(arg))

    @staticmethod
    def process_hint(hint, /):
        if hint in (_pempty, NotImplemented):
            return object
        if isinstance(hint, tuple):
            if len(hint) < 1:
                raise TypeError("Hint cannot be an empty tuple.")
            return hint
        if isinstance(hint, type):
            return hint
        if isinstance(hint, str):
            return OwnerGet(hint)
        raise TypeError(
            f"The `Field` hint must be a type or a tuple of types:",
            hint,
            )

    @staticmethod
    def process_note(note, /):
        if note in (_pempty, NotImplemented):
            return '?'
        return str(note)

    def __init__(self, /):
        super().__init__()
        self.degenerate = not bool(self.hint)

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

    def __directive_call__(self, body, name, /):
        body[self.__merge_name__][name] = self
        return name, _BoundObject(self)


###############################################################################
###############################################################################
