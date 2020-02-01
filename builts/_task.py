from types import FunctionType

from ._cycler import Cycler
from ._condition import Condition
from ._mutators import Mutator

class Task(Cycler, Condition, Mutator):
    def __init__(
            self,
            **kwargs
            ):
        super().__init__(status = self.status)
