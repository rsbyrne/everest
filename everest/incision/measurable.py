###############################################################################
''''''
###############################################################################


from .chora import Chora as _Chora


class Measurable(_Chora):

    metrictype = float

    def __init__(self, *args, metric, origin=None, limit=None, **kwargs):
        self.metric, self.origin, self.limit = metric, origin, limit
        self.register_argskwargs(metric=metric, origin=origin, limit=limit)
        super().__init__(*args, **kwargs)

    @classmethod
    def slice_start_methods(cls, /):
        yield cls.Element, cls.incise_measurable_origin
#         yield cls.metrictype, cls.incise_measurable

    def incise_measurable_origin(self, incisor, /):
        if self.origin is None:
            return self.new_self(origin=incisor)
        raise ValueError("Cannot reset origin.")


###############################################################################
###############################################################################
