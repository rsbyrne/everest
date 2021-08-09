###############################################################################
''''''
###############################################################################


import functools as _functools
import itertools as _itertools

from . import _utilities

from ._sliceable import Sliceable as _Sliceable

class Sampleable(_Sliceable):

    def __init__(self, *args, criterion, sampler=None, **kwargs):
        if sampler is not None:
            criterion = (criterion, sampler)
        super().__init__(*args, criterion=criterion, **kwargs)

    @classmethod
    def slice_methods(cls, /):
        yield (False, False, True), cls.incise_sampler_slice
        yield from super().slice_methods()

    def incise_sampler(self, sampler):
        '''Captures the sense of `self[::sampler]`'''
        return type(self)(
            *self.args,
            **(self.kwargs | dict(sampler=sampler)),
            )

    def incise_sampler_slice(self, _, __, sampler, /):
        return self.incise_sampler(sampler)


###############################################################################
###############################################################################
