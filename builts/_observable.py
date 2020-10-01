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
        self._observation_mode_active = False

        super().__init__(**kwargs)

    @contextmanager
    def _observation_mode(self):
        if self._observation_mode_active:
            yield None
        else:
            try:
                self._observation_mode_active = True
                temps = [fn() for fn in self._activate_observation_mode_fns]
                yield None
            finally:
                for temp, fn in zip(
                        temps,
                        self._deactivate_observation_mode_fns
                        ):
                    fn(temp)
                self._observation_mode_active = False
