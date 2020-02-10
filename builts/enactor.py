from ._cycler import Cycler

class Enactor(Cycler):

    script = '''_script_from everest.builts.enactor import Enactor as CLASS'''

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
