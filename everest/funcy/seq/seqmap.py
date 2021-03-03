################################################################################

from .seqoperation import SeqOperation as _SeqOperation
from . import _unpack_gruples

def mapple_op(ks, vs):
    return dict(_unpack_gruples(ks, vs))

class SeqMap(_SeqOperation):

    def __init__(self, keys, values, **kwargs):
        super().__init__(keys, values, op = mapple_op, **kwargs)

    def _titlestr(self):
        return '[Map]'

################################################################################
