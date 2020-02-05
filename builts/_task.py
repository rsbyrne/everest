import weakref

from ._cycler import Cycler
from ._boolean import Boolean

class Task(Boolean, Cycler):

    def __init__(
            self,
            _task_stop_metaFn = all,
            **kwargs
            ):

        self._task_cycler_fns = []
        self._task_stop_fns = []
        self._task_products = []

        super().__init__()

        self.promptees = dict()

        # Cycler attributes:
        def cycleFn():
            while not self:
                for fn in self._task_cycler_fns: fn()
                self.prompt_promptees()
        self._cycle_fns.append(cycleFn)

        # Boolean attributes:
        def boolFn():
            return _task_stop_metaFn([fn() for fn in self._task_stop_fns])
        self._bool_fns.append(boolFn)

    def add_promptee(self, obj):
        self.promptees[obj.hashID] = weakref.ref(obj)
    def remove_promptee(self, obj):
        del self.promptees[obj.hashID]
    def prompt_promptees(self):
        for hashID, ref in sorted(self.promptees.items()):
            promptee = ref()
            try: promptee()
            except: pass
