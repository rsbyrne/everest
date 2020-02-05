from ._cycler import Cycler

class Enactor(Cycler):
    from .enactor import __file__ as _file_
    def __init__(self, cycler, condition, **kwargs):
        self.cycler, self.condition = cycler, condition
        super().__init__(**kwargs)
        self._cycle_fns.append(self._enactor_cycleFn)
    def _enactor_cycleFn(self):
        if self.condition:
            self.cycler()
