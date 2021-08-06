###############################################################################
''''''
###############################################################################


import operator as _operator

from . import _classtools

from .bounded import Bounded as _Bounded
from .sampleable import Sampleable as _Sampleable


def make_comparator_from_gt(gt):
    def comparator(a, b):
        return gt(a, b) - gt(b, a)
    return comparator


class _Delimited_(_Bounded):

    def slice_in_range(self, start, stop):
        comparator, (lbnd, ubnd) = self.comparator, self.bnds
        if lbnd is None or start is None:
            lcheck = True
        else:
            lcheck = comparator(start, lbnd) > -1
        if ubnd is None or stop is None:
            ucheck = True
        else:
            ucheck = comparator(stop, ubnd) < 1
        return lcheck and ucheck

    def __contains__(self, item):
        if super().__contains__(item):
            comparator = self.comparator
            return all((
                comparator(item, self.lbnd) > -1, # item >= lbnd
                comparator(item, self.ubnd) < 0, # item < ubnd
                ))


class Orderable(_Sampleable):

    @classmethod
    def child_classes(cls):
        yield from super().child_classes()
        yield _Delimited_

    @classmethod
    def slice_methods(cls, /):
        for comb in ((True, True), (True, False), (False, True)):
            yield (*comb, False), cls.incise_delimit_slice
            yield (*comb, True), cls.incise_delimit_sample
        yield from super().slice_methods()

    def __init__(self, /, *args, comparator=None, gt=_operator.gt, **kwargs):
        if comparator is None:
            self.comparator = make_comparator_from_gt(gt)
            self.register_argskwargs(gt=gt)
        else:
            self.comparator = comparator
            self.register_argskwargs(comparator=comparator)
        super().__init__(*args, **kwargs)

    def slice_in_range(self, start, stop):
        return all(
            self.__contains__(st)
            for st in (start, stop) if st is not None
            )

    def incise_delimit(self, start, stop, /, *, context):
        if not self.slice_in_range(start, stop):
            raise KeyError("Slice out of range.")
        return self.Delimited(
            *self.args,
            **(self.kwargs | dict(lbnd=start, ubnd=stop)),
            )

    def incise_delimit_slice(self, start, stop, _, /, *, context):
        return self.incise_delimit(start, stop, context=context)

    def incise_delimit_sample(self, start, stop, step, /, *, context):
        return (
            self.incise_delimit(start, stop, context=context)
            .incise_sampler(step, context=context)
            )


Delimited = Orderable.Delimited


###############################################################################
###############################################################################
