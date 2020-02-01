from types import FunctionType

from everest.builts._task import Task as _Task

class Task(_Task):

    def __init__(
            self,
            prereq = True,
            iterator = None,
            stop = None,
            **kwargs
            ):
        super().__init__(prereq, iterator, stop, **kwargs)

CLASS = Task
build = CLASS.build
get = CLASS.get
