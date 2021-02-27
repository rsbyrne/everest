################################################################################

from .seqoperation import SeqOperation
from ..group import Gruple

def gruple_op(*args):
    return Gruple(args)

class SeqGroup(SeqOperation):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, op = gruple_op, **kwargs)

    def _titlestr(self):
        return '[Group]'

################################################################################
