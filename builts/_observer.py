from functools import wraps
from contextlib import contextmanager
import weakref
from collections import OrderedDict

from . import Built
from ._producer import Producer, Outs
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

class Observer(Built):

    def __init__(self,
            **kwargs
            ):

        self.subject = None
        self._obsConstruct = None
        self.observers = weakref.WeakKeyDictionary()

        super().__init__(**kwargs)

    @contextmanager
    @_unattached
    def observe(self, subject):
        try:
            self.subject = subject
            if not isinstance(self.subject, Observable):
                raise TypeError(
                    "Observee must be an instance of the Observable class."
                    )
            try:
                observer = self.observers[self.subject]
            except KeyError:
                observer = self.observer_construct(self.subject)
                self.observers[self.subject] = observer
            self.subject._observer = self
            yield observer
        finally:
            self.subject._observer = None
            self.subject = None
            self.observer = None

    @_attached
    def evaluate(self):
        return self.obsConstruct.evaluate()

    @property
    @_attached
    def obsConstruct(self):
        if self._obsConstruct is None:
            try:
                self._obsConstruct = self.observers[self.subject]
                if self._obsConstruct is None:
                    raise KeyError
            except KeyError:
                self._obsConstruct = self.observer_construct(self.subject)
                self.observers[self.subject] = self._obsConstruct
        return self._obsConstruct

    def observer_construct(self, subject):
        observer = self._observer_construct(subject.observables)
        return observer
    def _observer_construct(self, observables):
        return Grouper({})

    # def _prompt(self, prompter):
    #     # Overrides Promptable _prompt method:
    #     if self.subject is None:
    #         with self.attach(prompter):
    #             super()._prompt(prompter)
    #     elif prompter is self.subject:
    #         super()._prompt(prompter)
    #     else:
    #         raise AlreadyAttachedError
