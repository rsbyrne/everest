###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import itertools as _itertools
import functools as _functools

from . import _utilities

from ._meta import IncisableMeta as _IncisableMeta


_classtools = _utilities.classtools


_IncMethsLike = _collabc.Iterator[tuple[type, _collabc.Callable]]


def not_none(a, b):
    return b if a is None else a
overprint = _functools.partial(_itertools.starmap, not_none)


@_classtools.Diskable
@_classtools.MROClassable
class Incisable(metaclass=_IncisableMeta):

    @classmethod
    def _cls_extra_init_(cls, /):
        pass

    @classmethod
    def element_types(cls, /):
        return iter(())

    def incise_tuple(self, incisor, /):
        '''Captures the special behaviour implied by `self[a,b,c...]`'''
        raise TypeError("Tuple slicing not supported.")

    def incise_trivial(self, incisor=None, /):
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

    def __getitem__(self, incisor, /):
        try:
            meth = self.incmeths[type(incisor)]
        except KeyError as exc:
            raise TypeError from exc
        return meth(self, incisor)

    def new_self(self, *args, **kwargs):
        return type(self)(
            *overprint(_itertools.zip_longest(self.args, args)),
            **(self.kwargs | kwargs),
            )

    def __contains__(self, item):
        return isinstance(item, self.Element)


###############################################################################
###############################################################################
