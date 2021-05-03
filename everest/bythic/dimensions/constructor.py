###############################################################################
''''''
###############################################################################

from collections.abc import Iterable as _Iterable
from abc import (
    ABCMeta as _ABCMeta,
    abstractmethod as _abstractmethod,
    )

from . import (
    dimension as _dimension,
    primary as _primary,
    multi as _multi,
    abstract as _abstract,
    )

class DimMeta(_ABCMeta):
    def __getitem__(cls, arg):
        if isinstance(arg, tuple):
            return _multi.Multi(*arg)
        if isinstance(arg, dict):
            return _multi.Multi(**arg)
        if isinstance(arg, set):
            return _multi.Set(*arg)
        if isinstance(arg, slice):
            return _primary.Range.construct(arg)
        if isinstance(arg, _Iterable):
            return _primary.Arbitrary.construct(arg)
        raise TypeError(arg)
class Dim(_abstract.AbstractDimension, metaclass = DimMeta):
    @_abstractmethod
    def __iter__(self):
        '''Dimensions should be iterable.'''

_ = Dim.register(_dimension.Dimension)

###############################################################################
###############################################################################
