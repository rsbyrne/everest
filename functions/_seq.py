from collections.abc import Sequence

from ._base import Function
from ._base import \
    FunctionException, FunctionMissingAsset, NullValueDetected, EvaluationError

class Seq(Function, Sequence):

    def __init__(self, *args):
        super().__init__(*args)
    def _evaluate(self):
        return self.terms
    def __getitem__(self, index):
        return self.terms[index]
    def __len__(self):
        return len(self.terms)
    # def _hashID(self):
    #     return w_hash(tuple(get_hash(t) for t in self.terms))
