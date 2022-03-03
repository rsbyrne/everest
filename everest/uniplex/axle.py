###############################################################################
''''''
###############################################################################


from everest.utilities import pretty as _pretty

from everest.ptolemaic.sprite import Sprite as _Sprite

from .plexon import GroupPlexon as _GroupPlexon
from .table import TableLike as _TableLike, Table as _Table


class Axle(_TableLike, _GroupPlexon, metaclass=_Sprite):

    baseshape: tuple = (None,)
    index: object = None

    def table(self, /, name, baseshape=(), *args, **kwargs):
        selfbaseshape = self.baseshape
        baseshape = (*selfbaseshape, *baseshape)
        sub = self.sub(name, baseshape, *args, typ=_Table, **kwargs)
        sub.shape = (*self.shape, *sub.shape[len(selfbaseshape):])
        return sub

    def axle(self, /, name, baseshape=(), *args, **kwargs):
        selfbaseshape = self.baseshape
        baseshape = (*selfbaseshape, *baseshape)
        sub = self.sub(name, baseshape, *args, typ=Axle, **kwargs)
        sub.shape = (*self.shape, *sub.shape[len(selfbaseshape):])
        return sub

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

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.subs, p, cycle, root=root)


###############################################################################
###############################################################################
