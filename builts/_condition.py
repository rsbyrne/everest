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
        super().__init__(**kwargs)
        self._inquireFn = lambda: inquirer(arg)
        self._bool_fns.append(_inquireFn)
