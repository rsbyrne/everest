###############################################################################
''''''
###############################################################################

from collections.abc import Iterable as _Iterable

from . import (
    dimension as _dimension,
    primary as _primary,
    multi as _multi,
    )

def construct(cls, arg):
    if isinstance(arg, tuple):
        return _multi.Multi(*(cls[a] for a in arg)) # pylint: disable=E1136
    if isinstance(arg, dict):
        return _multi.Multi(**{k:cls[v] for k, v in arg.items()}) # pylint: disable=E1136
    if isinstance(arg, set):
        return _multi.Set(*(cls[a] for a in arg)) # pylint: disable=E1136
    if isinstance(arg, slice):
        return _primary.Range.construct(arg)
    if isinstance(arg, cls):
        return arg
    if isinstance(arg, _Iterable):
        return _primary.Arbitrary.construct(arg)
    raise TypeError(arg)

_dimension.DimensionMeta.__getitem__ = construct
Dim = _dimension.Dimension

###############################################################################
###############################################################################
