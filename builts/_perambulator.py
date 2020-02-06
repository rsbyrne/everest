from ._task import Task
from ._iterator import LoadFail

class Perambulator(Task):

    from .perambulator import __file__ as _file_

    def __init__(
            self,
            arg = None,
            state = None,
            express = False,
            **kwargs
            ):

        self.arg, self.state, self.express = arg, state
        self._expressChecked = False

        super().__init__(**kwargs)

        # Task attributes:
        self._task_cycler_fns.append(self._perambulator_task_cycle_fn)
        self._task_stop_fns.append(self._perambulator_task_stop_fn)

    def _perambulator_task_cycle_fn(self):
        if self.express and not self._expressChecked:
            try: self.arg.load(self.state)
            except LoadFail: self.arg()
            self._expressChecked = True
        else:
            self.arg()

    def _perambulator_task_stop_fn(self):
        return self.state(self.arg)
