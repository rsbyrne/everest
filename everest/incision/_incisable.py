###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta
import collections as _collections
from collections import abc as _collabc
import itertools as _itertools
import functools as _functools

from . import _utilities

from ._meta import IncisableMeta as _IncisableMeta


_classtools = _utilities.classtools
_TypeMap = _utilities.misc.TypeMap
_IncMethsLike = _collabc.Iterator[tuple[type, _collabc.Callable]]


def not_none(a, b):
    return b if a is None else a


overprint = _functools.partial(_itertools.starmap, not_none)


def passfn(arg, /):
    return arg




# class _Incision_:
#     ...


@_classtools.Diskable
# @_classtools.MROClassable
class Incisable(metaclass=_IncisableMeta):

    class _Element_(metaclass=_ABCMeta):

        __slots__ = ('index')

        def __init__(self, index):
            self.index = index

    class _Incisor_(metaclass=_ABCMeta):
        ...

    class _Retriever_(metaclass=_ABCMeta):
        ...

    @classmethod
    def child_classes(cls, /):
        return iter(())

    @classmethod
    def rider_classes(cls, /):
        yield cls._Element_
        yield cls._Incisor_
        yield cls._Retriever_

    @classmethod
    def element_types(cls, /):
        return iter(())

    @staticmethod
    def incise_generic(meth, obj, incisor, _, incise, /):
        return incise(meth(obj, incisor))

    def incise_tuple(self, incisor: tuple, /):
        '''Captures the special behaviour implied by `self[a,b,c...]`'''
        raise TypeError("Tuple slicing not supported.")

    def incise_trivial(self, incisor: type(Ellipsis) = None, /):
        '''Captures the special behaviour implied by `self[...]`.'''
        return self

    @classmethod
    def incision_methods(cls, /) -> _IncMethsLike:
        '''Returns acceptable incisor types and their associated getmeths.'''
        return iter(())

    @classmethod
    def priority_incision_methods(cls, /) -> _IncMethsLike:
        '''Returns like `.incision_methods` but takes priority.'''
        yield tuple, cls.incise_tuple
        yield type(Ellipsis), cls.incise_trivial

    @classmethod
    def get_incision_meths(cls, /) -> _TypeMap:
        pairs = _itertools.chain(
            cls.priority_incision_methods(),
            cls.incision_methods()
            )
        return _TypeMap(
            (key, _functools.partial(cls.incise_generic, meth))
            for key, meth in pairs
            )

    def retrieve_trivial(self, incisor: _Element_, /):
        '''Returns the element if this incisable contains it.'''
        if self.__contains__(incisor):
            return incisor
        raise ValueError(f"Element {incisor} not in {self}.")

    @staticmethod
    def retrieve_generic(meth, obj, incisor, retrieve, _, /):
        return retrieve(meth(obj, incisor))

    def retrieve_none(self, incisor: type(None), /):
        '''Returns what the user has asked for: nothing!'''
        return None

    @classmethod
    def retrieval_methods(cls, /) -> _IncMethsLike:
        '''Returns acceptable retriever types and their associated getmeths.'''
        return iter(())

    @classmethod
    def priority_retrieval_methods(cls, /) -> _IncMethsLike:
        '''Returns like `.retrieval_methods` but takes priority.'''
        yield type(None), cls.retrieve_none
        yield cls.Element, cls.retrieve_trivial

    @classmethod
    def get_retrieval_meths(cls, /) -> _TypeMap:
        pairs = _itertools.chain(
            cls.priority_retrieval_methods(),
            cls.retrieval_methods()
            )
        return _TypeMap(
            (key, _functools.partial(cls.retrieve_generic, meth))
            for key, meth in pairs
            )

    @classmethod
    def _cls_extra_init_(cls, /):
        Element = cls.Element
        for typ in cls.element_types():
            _ = Element.register(typ)
        retmeths = cls.retmeths = cls.get_retrieval_meths()
        Retriever = cls.Retriever
        for typ in retmeths:
            _ = Retriever.register(typ)
        incmeths = cls.incmeths = cls.get_incision_meths()
        Incisor = cls.Incisor
        for typ in incmeths:
            _ = Incisor.register(typ)
        cls.getmeths = _collections.ChainMap(retmeths, incmeths)

    def __getitem__(self, incisor, retrieve=passfn, incise=passfn, /):
        try:
            meth = self.getmeths[type(incisor)]
        except KeyError as exc:
            raise TypeError from exc
        return meth(self, incisor, retrieve, incise)

    def new_self(self, *args, cls=None, **kwargs):
        return (type(self) if cls is None else cls)(
            *overprint(_itertools.zip_longest(self.args, args)),
            **(self.kwargs | kwargs),
            )

    def __contains__(self, item):
        return isinstance(item, self.Element)


###############################################################################
###############################################################################
