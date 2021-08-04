###############################################################################
''''''
###############################################################################


from __future__ import annotations

from abc import ABCMeta as _ABCMeta
import itertools as _itertools
from collections import abc as _collabc
import typing as _typing
from functools import lru_cache as _lru_cache

from . import _classtools
from . import _utilities

_TypeMap = _utilities.misc.TypeMap


class ChoraMeta(_ABCMeta):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._cls_extra_init_()

    def _cls_extra_init_(cls):
        ...


class ElementMeta(_ABCMeta):

    def construct(cls, inp):
        return NotImplemented

    def __call__(cls, inp):
        '''Creates the Element.'''
        return cls.construct(inp)


@_classtools.MROClassable
@_classtools.Diskable
class Chora(
        metaclass=ChoraMeta
        ):

    comptypes = (object,)

    class _Incisor(metaclass=_ABCMeta):
        ...

    Incisor = _Incisor

    class _Element(metaclass=ElementMeta):
        comptypes = tuple()
        @classmethod
        @_lru_cache
        def __subclasshook__(cls, C):
            return all(issubclass(C, base) for base in cls.comptypes)

    Element = _Element

    @_classtools.Overclass
    class Incision:

        @_classtools.Overclass
        class BadIncision:
            def __init__(self, *args, **kwargs):
                raise ValueError(
                    f"Object of type {type(self)} "
                    f"cannot be incised with inputs *{args}, **{kwargs}"
                    )

    @classmethod
    def _cls_extra_init_(cls):

        comptypes = cls.comptypes = tuple(set(
            _itertools.chain.from_iterable(
                _itertools.chain.from_iterable(
                    ctyp.__mro__ for ctyp in base.comptypes
                    )
                for base in (cls, *cls.__bases__)
                if hasattr(base, 'comptypes')
                )
            ))

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

        cls.Incisor = type(
            f"{cls.__name__}Incisor",  # name
            (cls._Incisor,),  # bases
            dict(__subclasshook__=__subclasshook__),  # namespace
            )

        cls.Element = type(
            f"{cls.__name__}Element",  # name
            (cls._Element,),  # bases
            dict(comptypes=comptypes),  # namespace
            )

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

    def validate(self, inp):
        return True

    def retrieve(self, inp):
        '''Returns a single `Element` from inside the `Chora`.'''
        if self.validate(inp):
            return self.Element(inp)
        raise ValueError(inp)

    def __contains__(self, arg: _typing.Any) -> bool:
        '''Returns true if `arg` is a valid product of `cls`.'''
        if isinstance(arg, self.Element):
            return self.validate(arg)
        return False

    _IncMethsLike = _collabc.Iterator[tuple[type, _collabc.Callable]]

    @classmethod
    def incision_methods(cls) -> _IncMethsLike:
        '''Returns acceptable incisor types and their associated getmeths.'''
        yield cls.Element, cls.retrieve
        yield object, cls.Incision.BadIncision

    @classmethod
    def priority_incision_methods(cls) -> _IncMethsLike:
        '''Returns like `.incision_methods` but takes priority.'''
        return iter(())

    GetItemLike = _typing.Union[Incision, Element]

    def __getitem__(self, incisor: Incisor) -> GetItemLike:
        return self.incmeths[type(incisor)](self, incisor)


###############################################################################
###############################################################################
