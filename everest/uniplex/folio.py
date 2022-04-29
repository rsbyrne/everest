###############################################################################
''''''
###############################################################################


import functools as _functools

from everest.utilities import pretty as _pretty

from everest.ptolemaic.pentheros import Pentheros as _Pentheros

from .plexon import GroupPlexon as _GroupPlexon, SubPlexon as _SubPlexon
from .leaf import Leaf as _Leaf
from .table import Table as _Table
from .axle import Axle as _Axle
from .gable import Gable as _Gable


class FolioLike(_GroupPlexon):
    ...


class Folio(_SubPlexon, FolioLike, metaclass=_Pentheros):

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.subs, p, cycle, root=root)


for typ in (_Leaf, Folio, _Table, _Axle, _Gable):
    meth = _functools.partialmethod(FolioLike.sub, typ=typ)
    setattr(FolioLike, typ.__name__.lower(), meth)
del typ, meth


###############################################################################
###############################################################################
