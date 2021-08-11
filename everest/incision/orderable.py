###############################################################################
''''''
###############################################################################


import operator as _operator

from .chora import Chora as _Chora


def make_comparator_from_gt(gt):
    def comparator(a, b):
        return gt(a, b) - gt(b, a)
    return comparator


class Orderable(_Chora):

    def __init__(
            self, /, *args,
            comparator=None, gt=_operator.gt, lbnd=None, ubnd=None, **kwargs
            ):
        if not hasattr(self, 'comparator'):
            if comparator is None:
                self.comparator = make_comparator_from_gt(gt)
                self.register_argskwargs(gt=gt)
            else:
                self.comparator = comparator
                self.register_argskwargs(comparator=comparator)
        self.bnds = self.lbnd, self.ubnd = lbnd, ubnd
        if lbnd is not None:
            self.register_argskwargs(lbnd=lbnd)
        if ubnd is not None:
            self.register_argskwargs(ubnd=ubnd)
        super().__init__(*args, **kwargs)

    def incise_delimit_start(self, incisor, /):
        lbnd, ubnd, comparator = self.lbnd, self.ubnd, self.comparator
        if lbnd is not None:
            if comparator(incisor, lbnd) <= 0:
                return self
        if ubnd is not None:
            if comparator(incisor, ubnd) >= 0:
                incisor = ubnd
        if not self.__contains__(incisor):
            raise KeyError("Delimit out of range")
        return self.new_self(lbnd=incisor)

    def incise_delimit_stop(self, incisor, /):
        lbnd, ubnd, comparator = self.lbnd, self.ubnd, self.comparator
        if ubnd is not None:
            if comparator(incisor, ubnd) >= 0:
                return self
        if lbnd is not None:
            if comparator(incisor, lbnd) <= 0:
                incisor = lbnd
        if not self.__contains__(incisor):
            raise KeyError("Delimit out of range")
        return self.new_self(ubnd=incisor)

    @classmethod
    def slice_start_methods(cls, /):
        yield cls.Element, cls.incise_delimit_start
        yield from super().slice_start_methods()

    @classmethod
    def slice_stop_methods(cls, /):
        yield cls.Element, cls.incise_delimit_stop
        yield from super().slice_stop_methods()

    def item_in_range(self, item):
        lbnd, ubnd, comparator = self.lbnd, self.ubnd, self.comparator
        return all((
            True if lbnd is None else comparator(item, self.lbnd) >= 0,
            True if ubnd is None else comparator(item, self.ubnd) < 0,
            ))

    def __contains__(self, item):
        if not super().__contains__(item):
            return False
        return self.item_in_range(item)


###############################################################################
###############################################################################
