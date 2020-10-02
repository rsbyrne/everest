from . import Built

class Mutable(Built):

    def __init__(self,
            **kwargs
            ):

        self.mutables = dict()

        super().__init__(**kwargs)
