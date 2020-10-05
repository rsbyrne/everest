import builtins

from . import Built

class Boolean(Built):
    def __init__(
            self,
            _bool_op = 'all',
            **kwargs
            ):
        self._bool_op = getattr(builtins, _bool_op)
        super().__init__(**kwargs)
    def __bool__(self):
        return _bool_op([*self._bool_fn()][1:])
    def _bool_fn(self):
        yield None
