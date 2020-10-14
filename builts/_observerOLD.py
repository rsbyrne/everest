from functools import wraps
from contextlib import contextmanager
import weakref

from . import Built
from ._observable import Observable

from ..utilities import Grouper

from ..exceptions import EverestException
class ObserverError(EverestException):
    '''An error has emerged related to the Observer class.'''
class ObserverInputError(ObserverError):
    '''Observer subjects must be instances of Observable class.'''
class AlreadyAttachedError(ObserverError):
    '''Observer is already attached to that subject.'''
class NotAttachedError(ObserverError):
    '''Observer is not attached to a subject yet.'''
class NoObservables(ObserverError):
    '''Subject has no observables; it may need to be initialised first.'''

def _attached(func):
    @wraps(func)
    def wrapper(self, *args, silent = False, **kwargs):
        if self.subject is None and not silent:
            raise NotAttachedError
        return func(self, *args, **kwargs)
    return wrapper
def _unattached(func):
    @wraps(func)
    def wrapper(self, *args, silent = False, **kwargs):
        if not self.subject is None and not silent:
            raise AlreadyAttachedError
        return func(self, *args, **kwargs)
    return wrapper
def _observation_mode(func):
    @_attached
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self.subject._observation_mode():
            self.subject._outFns.append(self.observer.out)
            self.subject._producer_outkeys.append(self.observer.outkeys)
            self.subject._outputSubKeys.append(self._key)
            out = func(self, *args, **kwargs)
            self.subject._outputSubKeys.remove(self._key)
            return out
    return wrapper

class Observer(Built):

    def __init__(self,
            **kwargs
            ):

        # Expects:
        # self.build_observer

        self.subject = None
        self.observer = None
        self._observers = weakref.WeakKeyDictionary()

        super().__init__(**kwargs)

    @contextmanager
    @_unattached
    def observe(self, subject):
        try:
            if not isinstance(subject, Observable):
                raise TypeError(
                    "Observee must be an instance of the Observable class."
                    )
            try:
                observer = self._observers[subject]
            except KeyError:
                observer = self.master_build_observer(subject.observables)
                self._observers[subject] = observer
            self.subject = subject
            self.observer = observer
            yield observer
        finally:
            self.subject = None
            self.observer = None

    @_observation_mode
    def out(self, *args, **kwargs):
        return self.subject.out(*args, **kwargs)
    @_observation_mode
    def store(self, *args, **kwargs):
        self.subject.store(*args, **kwargs)
    @_observation_mode
    def save(self, *args, **kwargs):
        self.subject.save(*args, **kwargs)
        self.subject.writer.add(
            self,
            'observer',
            self.subject._outputMasterKey,
            self.subject._outputSubKey,
            )

    def _key(self):
        return '/'.join(['observations', self.hashID])
    @property
    def key(self):
        return self._key()

    def master_build_observer(self, observables):
        observerDict = self.build_observer(observables)
        if 'self' in observerDict:
            del observerDict['self']
        return Grouper(observerDict)

    def _prompt(self, prompter):
        # Overrides Promptable _prompt method:
        if self.subject is None:
            with self.attach(prompter):
                super()._prompt(prompter)
        elif prompter is self.subject:
            super()._prompt(prompter)
        else:
            raise AlreadyAttachedError
