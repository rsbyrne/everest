from . import Built
from .condition import Condition

class Task(Built):
    def __init__(self, startCondition, completeCondition):
        self.available = Condition()
        self.complete
