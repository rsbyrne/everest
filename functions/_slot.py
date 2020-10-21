from ._base import Function
from ._base import \
    FunctionException, FunctionMissingAsset, NullValueDetected, EvaluationError

class Slot(Function):

    def __init__(self, name = None):
        self._slots = 1
        super().__init__(name = name)
        if name is None:
            self._argslots = 1
            self._kwargslots = []
        else:
            self._argslots = 0
            self._kwargslots = [self.name]
    def close(self, *args, **kwargs):
        if len(args) + len(kwargs) > self._slots:
            raise FunctionException
        if len(args):
            return args[0]
        elif len(kwargs):
            if not kwargs.keys()[0] == self.name:
                raise KeyError
            return kwargs.values()[0]
        # raise FunctionException("Cannot close a Slot function.")
