###############################################################################
''''''
###############################################################################


from __future__ import annotations

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import itertools as _itertools
import weakref as _weakref
from collections import abc as _collabc
import typing as _typing

from . import _classtools
from . import _utilities

_TypeMap = _utilities.misc.TypeMap


# class IncisableMeta(_ABCMeta):

#     def __init__(cls, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         cls._cls_extra_init_()


class IncisorMeta(_ABCMeta):
    @property
    def owner(cls):
        return cls._owner()
class Incisor(metaclass=_ABCMeta):
    _owner = None


class Incision(metaclass = _ABCMeta):
    ...

class BadIncision(Incision):
    def __init__(self, *args, **kwargs):
        raise ValueError(
            f"Object of type {cls} "
            f"cannot be incised with inputs *{args}, **{kwargs}"
            )


class Element(metaclass = _ABCMeta):
    ...


@_classtools.MROClassable
@_classtools.Diskable
class Incisable(metaclass=_ABCMeta):

    Incisor = Incisor
    Incision = Incision
    BadIncision = BadIncision
    Element = Element

    incmeths = _utilities.misc.TypeMap(((object, BadIncision),))

    @classmethod
    def __init_subclass__(cls, **kwargs):

        cls.incmeths = cls._get_incmeths()

        @classmethod
        def __subclasshook__(inccls, C):
            if inccls is cls.Incisor:
                try:
                    incmeth = cls.incmeths[C]
                    if not issubclass(incmeth, BadIncision):
                        return True
                except KeyError:
                    pass
            return NotImplemented
        Incisor = cls.Incisor = type(
            f"{cls.__name__}Incisor", # name
            (cls.Incisor,), # bases
            dict(
                _owner = _weakref.ref(cls),
                __subclasshook__ = incisorcheck)
                , # namespace
            )

        GetItemLike = cls._GetItemLike = cls.Incision | cls.Element
        def __getitem__(self, incisor: Incisor) -> GetItemLike:
            return self.incmeths[type(incisor)](incisor)
        cls.__getitem__ = __getitem__

        super().__init_subclass__(**kwargs)

    @classmethod
    def _get_incmeths(cls) -> _TypeMap:
        return _TypeMap(
            _itertools.chain(
                cls.priority_incision_methods(),
                cls.incision_methods()
                ),
            defertos=(
                parent.incmeths for parent in cls.__bases__
                if hasattr(parent, 'incmeths')
                )
            )

    _IncMethsLike = _collabc.Iterator[tuple[type, _collabc.Callable]]
    @classmethod
    def incision_methods(cls) -> _IncMethsLike:
        '''Returns acceptable incisor types and their associated getmeths.'''
        return ()
    @classmethod
    def priority_incision_methods(cls) -> _IncMethsLike:
        '''Returns like `.incision_methods` but takes priority.'''
        return ()

    @_abstractmethod
    def __getitem__(self, arg: _typing.Any) -> _typing.NoReturn:
        raise NotImplementedError("No __getitem__ method on base class.")

#     def __getitem__(self, incisor: Incisor) -> Incision | Element:
#         return self.incmeths[type(incisor)](incisor)
        


###############################################################################
###############################################################################
