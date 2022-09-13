###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import types as _types

from everest.ur import Dat as _Dat
from everest.dclass import DClass as _DClass

from . import ptolemaic as _ptolemaic
from .sprite import Sprite as _Sprite
from .ousia import Ousia as _Ousia


class Member(metaclass=_DClass):

    note: str = None
    value: ... = None

    def __directive_call__(self, body, name, /):
        note, value = self.__params__
        newname = f"_{name}_value"
        if isinstance(value, (_types.MethodType, _types.FunctionType)):
            value.__name__ = newname
            value.__qualname__ = '.'.join((
                *'.'.split(value.__qualname__)[:-1], newname
                ))
            if note is None:
                note = value.__doc__
        if isinstance(value, property):
            if note is None:
                note = value.__doc__
        body['__enumerators__'][name] = note
        return newname, value

    @classmethod
    def __body_call__(cls, body, arg=None, /, **kwargs):
        if arg is None:
            return _functools.partial(cls.__body_call__, body, **kwargs)
        return cls(value=arg, **kwargs)


class Enumm(_Ousia):

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield '__enumerators__', dict

    @classmethod
    def _yield_bodymeths(meta, body, /):
        yield from super()._yield_bodymeths(body)
        yield 'member', _functools.partial(Member.__body_call__, body)

    @classmethod
    def body_handle_anno(meta, body, name, note, val, /):
        body[name] = Member(note, val)

    def __iter__(cls, /):
        return iter(cls._enumerators)

    def __contains__(cls, arg, /):
        return isinstance(arg, cls)

    ### Disabling redundant methods:

    @property
    def __call__(cls, /):
        raise TypeError("Cannot manually call an Enumm type.")


class _EnummBase_(metaclass=Enumm):

    __enumerators__ = {}
    __slots__ = ('serial', 'name', 'note')

    conservative = False

    ### Class setup:

    with escaped('methname'):
        for methname in (
                '_parameterise_',
                '_construct_',
                '_retrieve_',
                ):
            exec('\n'.join((
                f"@classmethod",
                f"def {methname}(cls, /, *_, **__):",
                f"    raise AttributeError(",
                f"        '{methname} not supported on Enumm types.'",
                f"        )",
                )))

    @classmethod
    def __class_get_signature__(cls, /):
        return None

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        enumerators = []
        enumeratorsdict = {}
        items = cls.__enumerators__.items()
        if cls.conservative:
            items = (
                (name, note) for name, note in items if not hasattr(cls, name)
                )
        for serial, (name, note) in enumerate(items):
            obj = cls._instantiate_(_Ousia.BaseTyp._parameterise_())
            obj.serial, obj.name, obj.note = serial, name, note
            setattr(cls, name, obj)
            cls._register_innerobj(name, obj)
            enumerators.append(obj)
            enumeratorsdict[name] = obj
        cls._enumerators = tuple(enumerators)
        cls._enumeratorsdict = _Dat.convert(enumeratorsdict)

    ### Representations:

    def _content_repr(self, /):
        return ', '.join(map(repr, self.__params__))

    def __repr__(self, /):
        return f"{self.rootrepr}.{self.__relname__}"

    def __class_getitem__(cls, arg: (int, str), /):
        if isinstance(arg, str):
            return cls._enumeratorsdict[arg]
        return cls._enumerators[arg]

    def __lt__(self, other, /):
        if isinstance(other, self.__ptolemaic_class__):
            return self.serial < other.serial
        return super().__lt__(other)

    def __gt__(self, other, /):
        if isinstance(other, self.__ptolemaic_class__):
            return self.serial > other.serial
        return super().__gt__(other)

    @property
    def value(self, /):
        return getattr(self, f"_{self.name}_value")


###############################################################################
###############################################################################
