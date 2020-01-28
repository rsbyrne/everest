from . import Built
from .condition import Condition

class Task(Built):
    def __init__(self, prerequisites, stopCondition):
        self.available = Condition()
        self.complete
