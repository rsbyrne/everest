###############################################################################
''''''
###############################################################################


from __future__ import annotations

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import itertools as _itertools
from collections import abc as _collabc
import typing as _typing

from . import _classtools
from . import _utilities

_TypeMap = _utilities.misc.TypeMap


class IncisableMeta(_ABCMeta):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._cls_extra_init_()

    def _cls_extra_init_(cls):
        ...


@_classtools.MROClassable
@_classtools.Diskable
class Incisable(
        metaclass=IncisableMeta
        ):

    class _Incisor(metaclass=_ABCMeta):
        ...

    @_classtools.Overclass
    class Incision:

        @_classtools.Overclass
        class BadIncision:
            def __init__(self, *args, **kwargs):
                raise ValueError(
                    f"Object of type {type(self)} "
                    f"cannot be incised with inputs *{args}, **{kwargs}"
                    )

    @_classtools.MROClass
    class Element:
        ...

    @classmethod
    def _cls_extra_init_(cls):

        cls.incmeths = cls._get_incmeths()

        @classmethod
        def __subclasshook__(inccls, C):
            if inccls is cls.Incisor:
                try:
                    incmeth = cls.incmeths[C]
                    if not issubclass(incmeth, cls.Incision.BadIncision):
                        return True
                except KeyError:
                    pass
            return NotImplemented

        Incisor = cls.Incisor = type(
            f"{cls.__name__}Incisor",  # name
            (cls._Incisor,),  # bases
            dict(__subclasshook__=__subclasshook__),  # namespace
            )

        GetItemLike = cls.GetItemLike = _typing.Union[
            cls.Incision, cls.Element
            ]

        def __getitem__(self, incisor: Incisor) -> GetItemLike:
            return self.incmeths[type(incisor)](incisor)

        cls.__getitem__ = __getitem__

#         super()._cls_extra_init_()

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
        yield object, cls.Incision.BadIncision

    @classmethod
    def priority_incision_methods(cls) -> _IncMethsLike:
        '''Returns like `.incision_methods` but takes priority.'''
        return ()

    @_abstractmethod
    def __contains__(self, arg: _typing.Any) -> bool:
        '''Checks if `arg` is 'contained' by `self`.'''
        raise NotImplementedError(
            f"Type {type(self)} must define __contains__"
            )


###############################################################################
###############################################################################
