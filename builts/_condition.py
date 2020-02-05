from types import FunctionType

from ._boolean import Boolean

class Condition(Boolean):
    from .condition import __file__ as _file_
    def __init__(
            self,
            inquirer = None,
            arg = None,
            **kwargs
            ):
        self.inquirer, self.arg = inquirer, arg
        super().__init__(**kwargs)
        # Boolean attributes:
        self._bool_fns.append(self._condition_boolFn)
    def _condition_boolFn(self):
        return self.inquirer(self.arg)
