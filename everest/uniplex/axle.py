###############################################################################
''''''
###############################################################################


import functools as _functools

from everest.utilities import pretty as _pretty

from everest.ptolemaic.compound import Compound as _Compound

from .plexon import GroupPlexon as _GroupPlexon
from .table import PseudoTableLike as _PseudoTableLike, Table as _Table
from .gable import Gable as _Gable


class Axle(_PseudoTableLike, _GroupPlexon, metaclass=_Compound):

    baseshape: tuple = (None,)
    # index: object = None

    def sub_tablelike(
            self, /, name, baseshape=(), *args, typ: type, **kwargs
            ):
        selfbaseshape = self.baseshape
        baseshape = (*selfbaseshape, *baseshape)
        sub = self.sub(name, baseshape, *args, typ=typ, **kwargs)
        sub.shape = (*self.shape, *sub.shape[len(selfbaseshape):])
        return sub

    def _update_shape(self, /):
        shape = self.shape
        for child in self.subs.values():
            child.shape = (*shape, *child.shape[len(shape):])

    def __setitem__(self, key, val, /):
        for sub, child in zip(zip(*val), self.subs.values()):
            child[key] = sub

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.subs, p, cycle, root=root)


for typ in (Axle, _Table, _Gable):
    meth = _functools.partialmethod(Axle.sub_tablelike, typ=typ)
    setattr(Axle, typ.__name__.lower(), meth)
del typ, meth


###############################################################################
###############################################################################
