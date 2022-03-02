###############################################################################
''''''
###############################################################################


from everest.ptolemaic.sprite import Sprite as _Sprite

from .plexon import GroupPlexon as _GroupPlexon, SubPlexon as _SubPlexon
from .leaf import Leaf as _Leaf
from .table import Table as _Table
from .axle import Axle as _Axle


class FolioLike(_GroupPlexon):

    def leaf(self, /, *args, **kwargs):
        return self.sub(*args, typ=_Leaf, **kwargs)

    def folio(self, /, *args, **kwargs):
        return self.sub(*args, typ=Folio, **kwargs)

    def table(self, /, *args, **kwargs):
        return self.sub(*args, typ=_Table, **kwargs)

    def axle(self, /, *args, **kwargs):
        return self.sub(*args, typ=_Axle, **kwargs)


class Folio(_SubPlexon, FolioLike, metaclass=_Sprite):

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        self.subs._repr_pretty_(p, cycle, root=root)


###############################################################################
###############################################################################
