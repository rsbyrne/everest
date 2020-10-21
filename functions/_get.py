from ..utilities import get_hash

from ._base import Function
from ._base import \
    FunctionException, FunctionMissingAsset, NullValueDetected, EvaluationError

class GetAttr(Function):

    def __init__(self,
            target,
            *props
            ):
        self.target, self.props = target, props
        super().__init__(target, *props)

    def _evaluate(self):
        target, *props = self.terms
        if target is None:
            raise ValueError
        target = self._value_resolve(target)
        for prop in props:
            prop = self._value_resolve(prop)
            target = getattr(target, prop)
        return target

    def _hashID(self):
        return '.'.join([
            get_hash(self.terms[0]),
            *[str(t) for t in self.terms[1:]]
            ])

class GetItem(Function):

    def __init__(self,
            target,
            key
            ):
        self.target, self.key = target, key
        super().__init__(target, key)

    def _evaluate(self):
        target, key = self.target, self.key
        target = self._value_resolve(target)
        key = self._value_resolve(key)
        return target[key]
