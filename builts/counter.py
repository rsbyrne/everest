from . import Built
from ..value import Value

class Counter(Built):
    def __init__(self, **kwargs):
        self.count = Value(0)
        super().__init__(**kwargs)
