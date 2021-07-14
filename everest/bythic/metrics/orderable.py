###############################################################################
''''''
###############################################################################


from . import _Sliceable


class Orderable(_Sliceable):
    ...


class Enumerable(Orderable):

    def __init__(self, step):
        self.step = step
        super().__init__()


class Commenceable(Orderable):

    def __init__(self, start):
        self.start = start
        super().__init__()


class Countable(Commenceable, Enumerable):
    ...


class Circumscribable(Commenceable):

    def __init__(self, start, stop, *args):
        super().__init__(start, *args)
        self.stop = stop

class Tractable(Circumscribable, Countable):

    def __init__(self, start, stop, step):
        super().__init__(start, stop, step)


###############################################################################
###############################################################################
