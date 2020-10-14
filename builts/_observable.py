from functools import wraps

from ._producer import Producer
from ..utilities import Grouper

from ..exceptions import EverestException
class ObservableError(EverestException):
    pass
class NoObserver(EverestException):
    pass

def _observation_mode(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return getattr(self.observer, func.__name__)(*args, **kwargs)
        except NoObserver:
            return func(self, *args, **kwargs)
    return wrapper

# class Obs:
#

class Observable(Producer):

    def __init__(self,
            **kwargs
            ):

        self.observables = Grouper({})
        self._observer = None

        super().__init__(**kwargs)

    def _outputSubKey(self):
        for o in super()._outputSubKey():
            yield o
        try:
            yield self.observer.hashID
        except NoObserver:
            yield ''

    @property
    def observer(self):
        if self._observer is None:
            raise NoObserver
        return self._observer

    def _save(self):
        super()._save()
        self._obs_save()
    @_observation_mode
    def _obs_save(self):
        pass
