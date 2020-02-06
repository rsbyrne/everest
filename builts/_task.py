import weakref

from ._cycler import Cycler
from ._boolean import Boolean
from ..weaklist import WeakList

class Task(Boolean, Cycler):

    def __init__(
            self,
            _task_stop_metaFn = all,
            **kwargs
            ):

        self._task_stop_metaFn = _task_stop_metaFn

        self._task_cycler_fns = WeakList()
        self._task_stop_fns = WeakList()
        self._task_products = WeakList()

        super().__init__(**kwargs)

        self.promptees = dict()

        # Cycler attributes:
        self._cycle_fns.append(self._task_cycleFn)

        # Boolean attributes:
        self._bool_fns.append(self._task_boolFn)

    def _task_cycleFn(self):
        while not self:
            for fn in self._task_cycler_fns: fn()
            self.prompt_promptees()

    def _task_boolFn(self):
        return self._task_stop_metaFn([fn() for fn in self._task_stop_fns])

    def add_promptee(self, obj):
        self.promptees[obj.hashID] = weakref.ref(obj)
    def remove_promptee(self, obj):
        del self.promptees[obj.hashID]
    def prompt_promptees(self):
        for hashID, ref in sorted(self.promptees.items()):
            promptee = ref()
            try: promptee()
            except: pass
