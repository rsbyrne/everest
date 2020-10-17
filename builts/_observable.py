from functools import wraps
import weakref

from ._producer import Producer
from ..utilities import Grouper
from ..weaklist import WeakList

from ..exceptions import *
class ObservableError(EverestException):
    pass
class ObservableMissingAsset(MissingAsset, ObservableError):
    pass
class NoObserver(EverestException):
    pass
class ObservationModeError(EverestException):
    pass

def _observation_mode(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return getattr(self.observer, func.__name__)(*args, **kwargs)
        except NoObserver:
            return func(self, *args, **kwargs)
    return wrapper

class Obs:
    def __init__(self, host):
        self._host = weakref.ref(host)
    @property
    def host(self):
        host = self._host()
        assert not host is None
        return host
    def __getattr__(self, key):
        if key in dir(self):
            return self.__dict__[key]
        else:
            return self._get_out(key)
    def _get_out(self, key):
        for observer in self.host.observers:
            try:
                with observer(self.host):
                    return self.host.outs[key]
            except KeyError:
                pass
        raise KeyError

class Observable(Producer):

    def __init__(self,
            **kwargs
            ):

        self.observables = Grouper({})
        self._observer = None
        self.observers = WeakList()
        self.obs = Obs(self)

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

    def _load(self, *args, **kwargs):
        if not self._observer is None:
            raise ObservationModeError(
                "Cannot load state while in Observer Mode."
                )
        else:
            super()._load(*args, **kwargs)

    @_observation_mode
    def evaluate(self):
        return self._evaluate()
    def _evaluate(self):
        raise ObservableMissingAsset
