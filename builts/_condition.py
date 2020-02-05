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
        inquire = lambda: inquirer(arg)
        self._bool_fns.append(inquire)
