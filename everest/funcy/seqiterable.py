################################################################################

from . import generic as _generic

from .exceptions import *

def show_iter_vals(iterable):
    i, ii = list(iterable[:10]), list(iterable[:11])
    content = ', '.join(str(v) for v in i)
    if len(ii) > len(i):
        content += ' ...'
    return f'[{content}]'

class SeqIterable(_generic.FuncySoftIncisable):

    __slots__ = '_seq',

    def __init__(self, seq, /, *args, **kwargs):
        self._seq = seq
        super().__init__(*args, **kwargs)
    @property
    def seq(self):
        return self._seq
    @property
    def seqLength(self):
        return self.seq._seqLength()
    @property
    def shape(self):
        return (self.seqLength,)
    def __iter__(self):
        return self.seq._iter()

    def __str__(self):
        return show_iter_vals(self)
    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.seq)})'

################################################################################
