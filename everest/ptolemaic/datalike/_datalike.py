###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod

from . import _classtools

from . import _Ptolemaic
from . import _ur


class DatalikeMeta(type(_Ptolemaic)):

    def instantiate(cls, *args, **kwargs):
        if issubclass(cls, _ur.Ur):
            return super().instantiate(*args, **kwargs)
        urcls = cls._choose_ur_class(*args, **kwargs)
        return urcls(*args, **kwargs)


@_classtools.MROClassable
class Datalike(_Ptolemaic, metaclass = DatalikeMeta):

    @classmethod
    @_abstractmethod
    def _choose_ur_class(cls, *args, **kwargs) -> _ur.Ur:
        '''Selects an appropriate Ur class based on input args and kwargs.'''
        raise TypeError("Abstract methods should not get called.")

    mroclasses = ('Var', 'Dat', 'Inc', 'Seq', 'Non')

    Var = _ur.Var
    Dat = _ur.Dat
    Inc = _ur.Inc
    Seq = _ur.Seq
    Non = _ur.Non

    dtype = type(None)


###############################################################################
###############################################################################
