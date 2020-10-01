from contextlib import contextmanager

from ._permutable import Permutable
from ..weaklist import WeakList

class Observable(Permutable):

    def __init__(self,
            **kwargs
            ):

        self.observables = dict()
        self._activate_observation_mode_fns = []
        self._deactivate_observation_mode_fns = []

        super().__init__(**kwargs)

    @contextmanager
    def _observation_mode(self):
        try:
            temps = [fn() for fn in self._activate_observation_mode_fns]
            yield None
        finally:
            for temp, fn in zip(temps, self._deactivate_observation_mode_fns):
                fn(temp)
