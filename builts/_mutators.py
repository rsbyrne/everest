from types import FunctionType

from . import Built
from ..writer import Writer

class Mutator(Built):
    def __init__(
            self,
            mutateDict : dict = None,
            update_MutateDict : FunctionType = None,
            **kwargs
            ):
        self.writer = None
        self._mutateDict = mutateDict
        self._update_mutateDict = update_MutateDict
        self._post_anchor_fns.append(self._update_writer)
        super().__init__(**kwargs)
    def _update_writer(self):
        self.writer = Writer(self.name, self.path)
    def mutate(self):
        self._check_anchored()
        self._update_mutateDict()
        self.writer.add(self._mutateDict, self.hashID)

# class Mutator(Built):
#     def __init__(self, append = False, redact = False, alter = False, **kwargs):
#         self.writer = Writer(append = append, redact = redact, alter = alter)
#         super().__init__(**kwargs)
#
# class Appender(Mutator):
#     def __init__(self, **kwargs):
#         super().__init__(append = True)
#
# class Redactor(Mutator):
#     def __init__(self, **kwargs):
#         super().__init__(redact = True)
#
# class Alterer(Mutator):
#     def __init__(self, **kwargs):
#         super().__init__(alter = True)
