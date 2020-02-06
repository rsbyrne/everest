import ast

from ._mutator import Mutator
from ._counter import Counter
from . import load
from . import Built

class Stampable(Mutator):

    def __init__(
        self,
        **kwargs
        ):

        self.stamps = [(self.hashID, 0),]
        self.localObjects['stamps'] = self.stamps

        super().__init__(**kwargs)

        # Mutator attributes:
        self._update_mutateDict_fns.append(self._stampable_update_mutateDict)

        # Built attributes:
        self._post_anchor_fns.append(self._stampable_update_stamps)

    def _stampable_update_stamps(self):
        loaded = self.reader[self.hashID, 'stamps']
        self.stamps = sorted(set(self.stamps))

    def _stampable_update_mutateDict(self):
        self._mutateDict['stamps'] = self.stamps

    def stamp(self, stamper):
        self.stamps.append((stamper.hashID, self.count()))
