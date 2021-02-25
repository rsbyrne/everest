################################################################################

from .base import Seq
from .arbitrary import Arbitrary
from .seqoperations import muddle
from ..special import unkint
from ..map import unpack_gruples

class SeqMap(Seq):

    def __init__(self,
            keys,
            values,
            **kwargs
            ):
        keys, values = (self._seqmap_proc_term(term) for term in (keys, values))
        super().__init__(keys, values, **kwargs)
    @staticmethod
    def _seqmap_proc_term(term):
        if type(term) is tuple:
            term = [term,]
        if not isinstance(term, Seq):
            term = Arbitrary(*term)
        return term

    def _iter(self):
        ks, vs = self._resolve_terms()
        for k, v in muddle([ks, vs]):
            yield dict(unpack_tuple(k, v))
    def _seqLength(self):
        return unkint

################################################################################
