from ._base import Function
from ._base import \
    FunctionException, FunctionMissingAsset, NullValueDetected, EvaluationError

class Thing(Function):
    def __init__(self, thing):
        self.thing = thing
        super().__init__(thing)
    def _evaluate(self):
        return self.thing
