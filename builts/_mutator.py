from types import FunctionType

from ._cycler import Cycler
from ._condition import Condition

class Mutator(Cycler):
    def __init__(
            self,
            mutateFn : FunctionType,
            mutateCondition : Condition,
            **kwargs
            ):
        pass
        # self._mutate = mutateFn
        # self.mutateCondition
        # def _cycle(self):
        #     if mutateCondition:
        #         self.mutate()
        # cycleFn = lambda:
        # super().__init__(
        #     self._cycle,
        #     **kwargs
        #     )
