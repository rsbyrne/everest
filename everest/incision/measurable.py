###############################################################################
''''''
###############################################################################


from .chora import Chora as _Chora


class Measurable(_Chora):

    def __init__(self, *args, metric, origin=None, limit=None, **kwargs):
        self.metric, self.origin, self.limit = metric, origin, limit
        self.register_argskwargs(metric=metric, origin=origin, limit=limit)
        super().__init__(*args, **kwargs)

    @classmethod
    def slice_start_methods(cls, /):
        yield 

    def incise_measurable_origin(self, incisor, /):
        


###############################################################################
###############################################################################
