###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect

from everest import ur as _ur

from .sprite import Sprite as _Sprite
from .utilities import BindableObject as _BindableObject


_pempty = _inspect._empty


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


@_BindableObject.register
class SmartAttr(metaclass=_Sprite):

    __slots__ = ('cachedname', 'degenerate')

    hint: (type, str, tuple)
    note: str

    MERGETYPE = _ur.DatDict

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls._mergename = f"__{cls.__name__.lower()}s__"

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        params = cls.Params(*args, **kwargs)
        return super().__class_call__(*(
            getattr(cls, f"process_{name}")(val)
            for name, val in params._asdict().items()
            ))

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
    def __bound_get__(self, instance: object, owner: type, name: str, /):
        raise NotImplementedError

    def __bound_set__(self, instance, name, value, /):
        raise AttributeError(
            f"Can't set attribute: {instance}, {name}"
            )

    def __bound_delete__(self, instance, name, /):
        raise AttributeError(
            f"Can't delete attribute: {instance}, {name}"
            )


###############################################################################
###############################################################################