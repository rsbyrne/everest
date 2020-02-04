from .. import Built
from ..vector import Vector

class Space(Built):
    def __init__(
            self,
            slice_vector_fn,

            **kwargs
            ):
        self._slice_vector_fn = slice_vector_fn
        super().__init__(**kwargs)
    def __getitem__(self, arg):
        out = self._slice_vector_fn(arg)
        if isinstance(out, Vector):
