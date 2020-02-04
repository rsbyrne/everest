from .. import Built

class Space(Built):
    def __init__(
            self,
            slice_vector_fn,
            **kwargs
            ):
        self._slice_vector_fn = slice_vector_fn
        super().__init__(**kwargs)
    def __getitem__(self, arg):
        return self._slice_vector_fn(arg)
