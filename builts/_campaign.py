from ._task import Task

class Campaign(Task):

    from .campaign import __file__as _file_

    def __init__(self,
            space = None,
            **kwargs
            ):

        self.space = space

        super().__init__(**kwargs)

        # Task attributes:
        self._task_initialise_fns.append(self._campaign_initialise_fn)
        self._task_cycler_fns.append(self._campaign_cycle_fn)
        self._task_stop_fns.append(self._campaign_stop_fn)
        self._task_finalise_fns.append(self._campaign_finalise_fn)

    def _campaign_initialise_fn(self):
        pass

    def _campaign_cycle_fn(self):
        pass

    def _campaign_stop_fn(self):
        pass

    def _campaign_finalise_fn(self):
        pass
