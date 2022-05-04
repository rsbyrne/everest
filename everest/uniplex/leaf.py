###############################################################################
''''''
###############################################################################


from everest.ptolemaic.compound import Compound as _Compound

from .plexon import SubPlexon as _SubPlexon


class Leaf(_SubPlexon, metaclass=_Compound):

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        self.attrs._repr_pretty_(p, cycle, root=root)


###############################################################################
###############################################################################