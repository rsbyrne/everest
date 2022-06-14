###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import functools as _functools

from everest import ur as _ur

from .sprite import Sprite as _Sprite
from .classbody import Directive as _Directive


_pempty = _inspect._empty


_passthru = lambda x: x


class SmartAttr(_Directive, metaclass=_Sprite):

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
    def __body_call__(cls, body, arg=None, /, **kwargs):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **kwargs)
        return cls(hint=arg, **kwargs)

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

    def __directive_call__(self, body, name, /):
        body[self.__merge_name__][name] = self


###############################################################################
###############################################################################
