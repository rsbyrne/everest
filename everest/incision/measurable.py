###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta
import functools as _functools
import operator as _operator

from .chora import Chora as _Chora
from .orderable import Orderable as _Orderable


def make_comparator(origin, metric):
    def comparator(a, b, o=origin, m=metric, /):
        return m(o, b) - m(o, a)
    return comparator

def make_metric(comparator):
    def metric(a, b, comparator=comparator, /):
        return abs(comparator(a, b))


class _Originated_(_Orderable):

    metrictype = type(None)

    def __init__(
            self, /, *args,
            origin, metric=None, comparator=_operator.gt,
            lbnd=None, ubnd=None,
            **kwargs
            ):
        self.origin = origin
        self.register_argskwargs(origin=origin)
        if metric is None:
            self.metric = make_metric(comparator)
            self.register_argskwargs(comparator)
        else:
            self.metric = metric
            self.register_argskwargs(metric=metric)
            comparator = self.comparator = make_comparator(origin, metric)
        pos = self.pos = _functools.partial(comparator, origin)
        if lbnd is None:
            lbnd = pos(origin)
        elif isinstance(lbnd, self.Element):
            lbnd = pos(lbnd)
        ubnd = pos(ubnd) if isinstance(ubnd, self.Element) else ubnd
        super().__init__(*args, lbnd=lbnd, ubnd=ubnd, **kwargs)

    def process_relative_metric_incisor(self, incisor):
        lbnd, ubnd = self.bnds
        return incisor + lbnd if incisor > 0 else incisor + ubnd

    def process_element_to_metric(self, incisor):
        return self.metrictype(self.pos(incisor))

    def incise_measurable_origin(self, incisor, /):
        raise ValueError("Resetting of origin is forbidden.")

    def incise_metric_start_absolute(self, incisor, /):
        lbnd, ubnd = self.bnds
        incisor = max(lbnd, min(ubnd, incisor))
        if incisor == lbnd:
            return self
        return self.new_self(lbnd=incisor)

    def incise_delimit_start(self, incisor, /):
        incisor = self.process_element_to_metric(incisor)
        return self.incise_metric_start_absolute(incisor)

    def incise_metric_start(self, incisor, /):
        incisor = self.process_relative_metric_incisor(incisor)
        return self.incise_metric_start_absolute(incisor)

    @classmethod
    def slice_start_methods(cls, /):
        yield cls.metrictype, cls.incise_metric_start
        yield from super().slice_start_methods()

    def incise_metric_stop_absolute(self, incisor, /):
        lbnd, ubnd = self.bnds
        incisor = max(lbnd, incisor)
        if ubnd is not None:
            incisor = min(ubnd, incisor)
        if incisor == ubnd:
            return self
        return self.new_self(ubnd=incisor)

    def incise_delimit_stop(self, incisor, /):
        incisor = self.process_element_to_metric(incisor)
        return self.incise_metric_stop_absolute(incisor)

    def incise_metric_stop(self, incisor, /):
        incisor = self.process_relative_metric_incisor(incisor)
        return self.incise_metric_stop_absolute(incisor)

    @classmethod
    def slice_stop_methods(cls, /):
        yield cls.metrictype, cls.incise_metric_stop
        yield from super().slice_stop_methods()

    def item_in_range(self, item):
        pos = self.pos(item)
        return pos >= self.lbnd and pos < self.ubnd


class Measurable(_Chora):

    metrictype = type(None)
    _Originated_ = _Originated_

    @classmethod
    def child_classes(cls, /):
        yield from super().child_classes()
        yield cls._Originated_, dict(metrictype=cls.metrictype)

    def __init__(self, /, *args, metric=None, **kwargs):
        if not hasattr(self, 'metric'):
            if metric is None:
                raise ValueError("Must provide a value for 'metric'.")
            self.metric = metric
            self.register_argskwargs(metric=metric)
        super().__init__(*args, **kwargs)

    def incise_measurable_origin(self, incisor, /):
        return self.new_self(cls=self.Originated, origin=incisor)

    @classmethod
    def slice_start_methods(cls, /):
        yield from super().slice_start_methods()
        yield cls.Element, cls.incise_measurable_origin


###############################################################################
###############################################################################
