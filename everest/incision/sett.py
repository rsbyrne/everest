###############################################################################
''''''
###############################################################################


import functools as _functools
import collections.abc as _collabc

from . import _utilities

from .sliceable import Sliceable as _Sliceable


def always_true(arg):
    return True


class Sett(_Sliceable):

    def __init__(self, criteria0=always_true, /, *criteria):
        criteria = self.criteria = (criteria0, *criteria)
        self.criterion_function = \
            _utilities.process_criterion(list(criteria))
        self.register_argskwargs(*criteria)
        super().__init__()

    @property
    def __contains__(self):
        return self.criterion_function

    @classmethod
    def slice_methods(cls, /):
        yield (type(None), type(None), _collabc.Callable), cls.incise_sampler
        yield from super().slice_methods()

    def incise_sampler(self, sampler):
        return self.new_self(*self.criteria, sampler)


###############################################################################
###############################################################################
