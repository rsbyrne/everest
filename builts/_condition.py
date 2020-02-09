from types import FunctionType

from ._boolean import Boolean

class Condition(Boolean):
    global _file_
    def __init__(
            self,
            inquirer = None,
            arg = None,
            inv = False,
            **kwargs
            ):
        self.inquirer, self.arg, self.inv = inquirer, arg, inv
        super().__init__(**kwargs)
        # Boolean attributes:
        self._bool_fns.append(self._condition_boolFn)
    def _condition_boolFn(self):
        truth = self.inquirer(self.arg)
        if self.inv: truth = not truth
        return truth

from .condition import __file__ as _file_
