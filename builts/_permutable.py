from . import Built

class Permutable(Built):

    def __init__(self,
            **kwargs
            ):

        self.permutables = dict()

        super().__init__(**kwargs)
