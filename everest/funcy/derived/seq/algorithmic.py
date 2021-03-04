################################################################################

from functools import cached_property

from .seq import Seq as _Seq

class _Algorithmic(_Seq):
    _algorithm = None
    @cached_property
    def n(self):
        return self.Fn(0, name = 'n')
    @cached_property
    def algorithm(self):
        return self._algorithm.close(_seq_n = self.n)
    def _iter(self):
        self.n.value = -1
        while True:
            self.n += 1
            yield self.algorithm.value
    def _seqLength(self):
        return inf

class Algorithmic(_Algorithmic):
    def __init__(self, algorithm):
        self._algorithm = algorithm
        super().__init__(self.algorithm)

################################################################################
