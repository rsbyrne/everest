import numpy as np

from ..utilities import is_numeric

from ._base import Function
from ._base import \
    FunctionException, FunctionMissingAsset, NullValueDetected, EvaluationError

class Array(Function):

    def __init__(self,
            arg,
            initial = None,
            name = None
            ):

        super().__init__(
            arg,
            initial = initial,
            name = name
            )

        if isinstance(arg, Function):
            initial = np.array(initial)
            null = False
            pipe = arg
            value = initial
        else:
            if initial == 'null':
                null = True
            elif initial is None:
                null = False
            else:
                raise ValueError
            pipe = None
            value = np.array(arg)

        self._null = null
        self._value = value
        self.dtype = value.dtype
        self.pipe = pipe

    def _isnull(self):
        return self._null

    def __setattr__(self, key, value):
        if key == 'value':
            if value is None:
                super().__setattr__('_null', True)
                return None
            else:
                try:
                    self._value[...] = value
                    super().__setattr__('_null', False)
                except TypeError:
                    raise TypeError((value, type(value)))
                return None
        else:
            super().__setattr__(key, value)

    def _evaluate(self):
        if not self.pipe is None:
            addVal = self._value_resolve(self.pipe)
            self._value = np.append(self._value, addVal)
        if self.null: raise NullValueDetected(self._value)
        return self._value

    def _reassign(self, arg, op = None):
        if self.pipe is None:
            self.value = self._operate(arg, op = op).value
            return self
        else:
            return Value(self.pipe + arg, **self.kwargs)
    def __iadd__(self, arg): return self._reassign(arg, op = 'add')
    def __ifloordiv__(self, arg): return self._reassign(arg, op = 'floordiv')
    def __imod__(self, arg): return self._reassign(arg, op = 'mod')
    def __imul__(self, arg): return self._reassign(arg, op = 'mul')
    def __ipow__(self, arg): return self._reassign(arg, op = 'pow')
    def __isub__(self, arg): return self._reassign(arg, op = 'sub')
    def __itruediv__(self, arg): return self._reassign(arg, op = 'truediv')

    def pipein(self, arg):
        if not isinstance(arg, Function):
            raise FunctionException
        return Array(
            arg,
            initial = self._value,
            name = self.name
            )

    def _hashID(self):
        return self.name
