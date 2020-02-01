from types import FunctionType

from ._cycler import Cycler
from ._condition import Condition
from ..exceptions import EverestException

class TaskPrerequisiteNotMetError(EverestException):
    '''The prerequisite to commence this task \
has not been met yet.'''
    pass
class TaskStopMetError(EverestException):
    '''The task has been completed.'''
    pass

class Task(Condition, Cycler):

    def __init__(
            self,
            _task_prerequisite : Condition,
            _task_cycler : Cycler,
            _task_stop : Condition,
            **kwargs
            ):

        if not _task_prerequisite:
            if isinstance(_task_prerequisite, Task):
                _task_prerequisite()
            else:
                raise TaskPrerequisiteNotMetError

        assert _task_prerequisite

        super().__init__()

        # Condition attributes:
        self._bool_fns.append(lambda: _task_stop)

        # Cycler attributes:
        def cycle():
            if self:
                raise TaskStopMetError
            while not self:
                _task_cycler()
        self._cycle_fns.append(cycle)
