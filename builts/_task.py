from types import FunctionType

from . import Built
# from ._cycler import Cycler

class Task(Built):
    def __init__(
            self,
            prerequisites,
            makeFn,
            stopCondition,
            bailCondition,
            **kwargs
            ):

        super().__init__(status = self.status)
