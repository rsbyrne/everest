from functools import wraps
import weakref

from ._producer import Producer
from . import Meta
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
            self._observation_mode_hook()
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
        for observerClass in self.host.observerClasses:
            observer = observerClass()
            if not observer in self.host.observers:
                self.host.observers.append(observer)
            try:
                with observer(self.host):
                    return self.host.outs[key]
            except KeyError:
                pass
        raise KeyError

class Observable(Producer):

    def __init__(self,
            _observerClasses = [],
            **kwargs
            ):

        self.observables = Grouper({})
        self._observer = None
        self.observers = WeakList()
        self.observerClasses = WeakList()
        self.observerClasses.extend(_observerClasses)
        if 'observers' in self.ghosts:
            self.observerClasses.extend(self.ghosts['observers'])
        self.obs = Obs(self)

        super().__init__(**kwargs)

    def _observation_mode_hook(self):
        pass

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

    @_observation_mode
    def evaluate(self):
        return self._evaluate()
    def _evaluate(self):
        raise ObservableMissingAsset

    def _store(self, *args, **kwargs):
        super()._store(*args, **kwargs)
        if self._observer is None:
            for observer in self.observers:
                with observer(self):
                    super().store(*args, **kwargs)
    def _save(self, *args, **kwargs):
        super()._save(*args, **kwargs)
        if self._observer is None:
            for observer in self.observers:
                with observer(self):
                    super().save(*args, **kwargs)
                    self.writeouts.add(observer, 'observer')
    def _clear(self, *args, **kwargs):
        super()._clear(*args, **kwargs)
        if self._observer is None:
            for observer in self.observers:
                with observer(self):
                    self._clear(*args, **kwargs)

    def _load(self, *args, **kwargs):
        if not self._observer is None:
            raise ObservationModeError(
                "Cannot load state while in Observer Mode."
                )
        super()._load(*args, **kwargs)
