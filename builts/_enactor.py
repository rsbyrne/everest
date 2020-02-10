from ._cycler import Cycler

class Enactor(Cycler):

    from .enactor import __file__ as _file_

    def __init__(self,
            callable = None,
            condition = None,
            **kwargs
            ):
        self.callable, self.condition = callable, condition
        super().__init__(**kwargs)
        self._cycle_fns.append(self._enactor_cycleFn)

    def _enactor_cycleFn(self):
        if self.condition: self.callable()
