###############################################################################
''''''
###############################################################################


class Params:
    __slots__ = 'args', 'kwargs'

    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

    def __repr__(self):
        return type(self).__name__ + f"({self.args}, {self.kwargs})"


###############################################################################
###############################################################################
