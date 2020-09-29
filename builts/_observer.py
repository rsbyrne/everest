from ._observable import observable
from ._callable import callable

from ..exceptions import EverestException
class ObserverInputError(EverestException):
    '''Observer subjects must be instances of Observable class.'''

class Observable(Callable):

    def __init__(self,
            **kwargs
            ):

        # Expects:
        # self.subject
        # self.observe
        if not isinstance(self.subject, Observable):
            raise ObserverInputError

        self.observables = dict()

        super().__init__(**kwargs)

        # Callable attributes:
        self._call_fns.append(self._observable_call)

    def _observable_call(self):
        pass
