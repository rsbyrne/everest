from . import Built
from ..value import Value

class Counter(Built):
    def __init__(self):
        self.count = Value(0)
        super().__init__()
