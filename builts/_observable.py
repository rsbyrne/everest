from ._permutable import Permutable

class Observable(Permutable):

    def __init__(self,
            **kwargs
            ):

        self.observables = dict()

        super().__init__(**kwargs)
