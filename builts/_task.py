from . import Built
from ._condition import Condition
from ._cycler import Cycler

class Task(Condition):
    def __init__(
            self,
            prerequisites,
            cycler : Cycler,
            stopCondition,
            bailCondition
            ):
        self.available = Condition()
        self.complete
        super().__init__(lambda: bool(stopCondition))
