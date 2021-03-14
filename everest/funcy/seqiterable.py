################################################################################

from collections.abc import Iterable as _Iterable
from functools import lru_cache as _lru_cache
import itertools as _itertools

from . import generic as _generic

from .exceptions import *

def show_iter_vals(iterable):
    i, ii = list(iterable[:10]), list(iterable[:11])
    content = ', '.join(str(v) for v in i)
    if len(ii) > len(i):
        content += '...'
    return f'[{content}]'

class IterSlice(_Iterable, _generic.FuncySequence):
    def __init__(self, seq, start, stop, step):
        self.seq = seq
        self.start, self.stop, self.step = start, stop, step
    def __iter__(self):
        return _itertools.islice(self.seq, self.start, self.stop, self.step)
    def __getitem__(self, key):
        if type(key) is slice:
            return _itertools.islice(self, key.start, key.stop, key.step)
        else:
            return (v[key] for v in self)
    def __str__(self):
        return show_iter_vals(self)
    def __repr__(self):
        return f'IterSlice == {str(self)}'

class SeqIterable(_Iterable, _generic.FuncySequence):

    __slots__ = (
        'seq',
        )

    def __init__(self, seq):
        self.seq = seq

    def __iter__(self):
        return self.seq._iter()
    def __len__(self):
        return self.seq._seqLength()

    def __getitem__(self, arg):
        if isinstance(arg, slice):
            return self._get_slice(arg.start, arg.stop, arg.step)
        elif type(arg) is tuple:
            return self._get_tuple(arg)
        else:
            return self._get_index(arg)
    # @_lru_cache
    def _get_tuple(self, target):
        out = self
        for st in target:
            out = out[st]
        return out
    @_lru_cache
    def _get_index(self, target):
        it, i = iter(self), -1
        try:
            while i < target:
                i += 1
                val = next(it)
            try:
                return val
            except NameError:
                raise IndexError
        except StopIteration:
            raise IndexError(target)
    @_lru_cache
    def _get_slice(self, start, stop, step):
        return IterSlice(self, start, stop, step)

    def __str__(self):
        return show_iter_vals(self)
    def __repr__(self):
        return f'SeqIterable({repr(self.seq)}) == {str(self)}'

################################################################################
