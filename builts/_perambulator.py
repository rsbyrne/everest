from ._task import Task
from .states import State
from .states import threshold
from ._iterator import Iterator

class Perambulator(Task):

    from .perambulator import __file__ as _file_

    @staticmethod
    def _process_inputs(inputs):
        state = inputs['state']
        if not isinstance(state, State):
            if type(state) is int: prop = 'count'
            elif type(state) is float: prop = 'chron'
            else: raise TypeError
            inputs['state'] = threshold.build(
                prop = prop,
                op = 'ge',
                val = state
                )
        if not isinstance(inputs['iterator'], Iterator): raise TypeError

    def __init__(
            self,
            iterator = None,
            state = None,
            express = False,
            **kwargs
            ):

        self.iterator, self.state, self.express = \
            iterator, state, express
        self._expressChecked = False

        super().__init__(**kwargs)

        # Task attributes:
        self._task_initialise_fns.append(self._perambulator_task_save_fn)
        self._task_cycler_fns.append(self._perambulator_task_cycle_fn)
        self._task_stop_fns.append(self._perambulator_task_stop_fn)
        self._task_finalise_fns.append(self._perambulator_task_save_fn)

    def _perambulator_task_cycle_fn(self):
        if self.express and not self._expressChecked:
            from ._iterator import LoadFail
            try: self.iterator.load(self.state)
            except LoadFail: self.iterator()
            self._expressChecked = True
        else:
            self.iterator()

    def _perambulator_task_stop_fn(self):
        return self.state(self.iterator)

    def _perambulator_task_save_fn(self):
        if self.anchored:
            self.iterator.store()
            self.iterator.save()
