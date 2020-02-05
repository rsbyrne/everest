import operator

from . import State

class BoolOperator(State):
    from .booloperator import __file__ as _file_
    def __init__(
            self,
            prop : str = 'count',
            op : str = 'eq',
            val = None,
            **kwargs
            ):
        self.operation = getattr(operator, op)
        self.prop, self.val = prop, val
        super().__init__(self._boolFn, **kwargs)

    def _boolFn(self, arg):
        return bool(self.operation(getattr(arg, self.prop), self.val))
