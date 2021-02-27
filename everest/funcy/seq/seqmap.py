################################################################################

from .seqoperation import SeqOperation
from .seqgroup import SeqGroup
from ..map import unpack_gruples

def mapple_op(ks, vs):
    return dict(unpack_gruples(ks, vs))

class SeqMap(SeqOperation):

    def __init__(self, keys, values, **kwargs):
        super().__init__(keys, values, op = mapple_op, **kwargs)

    def _titlestr(self):
        return '[Map]'

################################################################################
