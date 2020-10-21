from ._base import Function
from ._base import \
    FunctionException, FunctionMissingAsset, NullValueDetected, EvaluationError

from ..exceptions import *

class Text(Function):

    def __init__(self, *args, **kwargs):
        raise NotYetImplemented
