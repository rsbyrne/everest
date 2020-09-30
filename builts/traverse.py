from ._task import Task
from ._wanderer import Wanderer

class Traverse(Task):

    _swapscript = '''from everest.builts.traverse import Traverse as CLASS'''

    @staticmethod
    def _process_inputs(inputs):
        if not isinstance(inputs['wanderer'], Wanderer):
            raise TypeError(
                "Main input must inherit from Everest Wanderer class"
                )
        return inputs

    def __init__(self,
            wanderer,
            start,
            stop,
            **kwargs
            ):

        super().__init__(**kwargs)

        # Task attributes:
        self._task_initialise_fns.append(self._traverse_initialise)
        self._task_cycler_fns.append(self._traverse_iterate)
        self._task_stop_fns.append(self._traverse_stop)
        self._task_finalise_fns.append(self._traverse_finalise)
