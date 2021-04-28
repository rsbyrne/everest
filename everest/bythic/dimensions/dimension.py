###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from collections import abc as _collabc

from . import _special

from .exceptions import *

def unpack_slice(slc):
    return (slc.start, slc.stop, slc.step)


class DimIterator(_collabc.Iterator):

    __slots__ = ('gen',)

    def __init__(self, iter_fn, /):
        self.gen = iter_fn()
        super().__init__()

    def __next__(self):
        return next(self.gen)

    def __repr__(self):
        return f"{__class__.__name__}({repr(self.gen)})"


def calculate_len(dim):
    raise NotYetImplemented

def raise_uniterable():
    raise DimensionUniterable


class Dimension(_ABC):

    mroclasses = 'DimIterator'
    DimIterator = DimIterator
    iterlen = _special.unkint
    iter_fn = raise_uniterable

    def __iter__(self):
        return DimIterator(self.iter_fn)

    def __len__(self):
        iterlen = self.iterlen
        if isinstance(iterlen, _special.InfiniteInteger):
            raise DimensionInfinite
        if isinstance(iterlen, _special.Unknown):
            iterlen = self.iterlen = calculate_len(self)
        return iterlen

    # def __getitem__(self, arg):
    #     if isinstance(arg, slice):
    #         return ISlice(self, arg)
    #     if isinstance(arg, int):
    #         if arg < 0:
    #             arg = len(self) + arg
    #         return Collapsed(self, arg)
    #     raise TypeError(type(arg))


class Tandem(Dimension):

    __slots__ = ('metrics',)

    def __init__(self, *args):
        metrics = []
        for arg in args:
            if isinstance(arg, tuple):
                metrics.extend(arg)
            elif isinstance(arg, Dimension):
                metrics.append(arg)
            else:
                raise TypeError(type(arg))
        metrics = self.metrics = tuple(metrics)
        self.iterlen = min(len(met) for met in metrics)
        super().__init__()

    def iter_fn(self):
        return zip(*self.metrics)


###############################################################################

# def inquirer(start, stop, step, dimlen):
#     print((start, stop, step), dimlen)
#     mylist = list(range(dimlen))
#     print("incorrect length:", get_slice_length(start, stop, step, dimlen))
#     mycut = mylist[start:stop:step]
#     print("correct length:", len(mycut))
#     start, stop, step = proper = slice(start, stop, step).indices(dimlen)
#     print("proper indices:", proper)
#     print(mycut)
#
# for dimlen in range(10):
#     alist = list(range(dimlen))
#     for start in range(-10, 10):
#         for stop in range(-10, 10):
#             for step in range(-10, 10):
#                 if not step:
#                     continue
#                 a = len(alist[start: stop: step])
#                 b = get_slice_length(start, stop, step, dimlen)
#                 if a != b:
#                     inquirer(start, stop, step, dimlen)
#                     print('\n')

#             for step in range(-3, 3):
#                 if not step == 0:
#                     a = len(alist[start:stop:step])
#                     b = get_slice_length(sstart, sstop, step, dimlen)
#                     if a != b:
#                         print(a, b, (start, stop, step), dimlen)
#                     assert a == b, (a, b, (start, stop, step), dimlen)
#                     a = len(list(range(dimlen))[start:stop:step])
#                     b = get_slice_length(start, stop, step, dimlen)
#                     if a != b:
#                         print(a, b, (start, stop, step), dimlen)

# mydim = Transform(Range(10, 30, 1.5), round)[3: 9] -> [14, 16, 18, 19, 20, 22]


###############################################################################
