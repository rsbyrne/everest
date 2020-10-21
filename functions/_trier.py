from ._base import Function
from ._base import \
    FunctionException, FunctionMissingAsset, NullValueDetected, EvaluationError

class Trier(Function):
    def __init__(self, func, exc = Exception, altval = None):
        if not isinstance(func, Function):
            raise TypeError
        if not (isinstance(exc, Exception) or issubclass(exc, Exception)):
            raise TypeError
        self.func, self.exc, self.altval = func, exc, altval
        super().__init__(func, exc = exc, altval = altval)
    def _evaluate(self):
        try:
            return func.value
        except self.exc:
            return altval
