###############################################################################
''''''
###############################################################################


from everest.ptolemaic.ousia import Ousia as _Ousia

from .plexon import GroupPlexon as _GroupPlexon
from .table import TableLike as _TableLike, Table as _Table


class Axle(_TableLike, _GroupPlexon, metaclass=_Ousia):

    _req_slots__ = ('index',)

    def __init__(self, /, parent, shape=(), index=None, *args, **kwargs):
        super().__init__(parent, shape, *args, **kwargs)
        self.index = None

    def table(self, /, name, shape=(), *args, **kwargs):
        shape = (*self.shape, *shape)
        return self.sub(name, shape, *args, typ=_Table, **kwargs)

    def axle(self, /, name, shape=(), *args, **kwargs):
        shape = (*self.shape, *shape)
        return self.sub(name, shape, *args, typ=Axle, **kwargs)

    def _update_shape(self, /):
        shape = self.shape
        for child in self.subs.values():
            child.shape = (*shape, *child.shape[len(shape):])

    def __setitem__(self, key, val, /):
        if isinstance(key, str):
            super().__setitem__(key, val)
        else:
            for sub, child in zip(zip(*val), self.subs.values()):
                child[key] = sub


###############################################################################
###############################################################################
