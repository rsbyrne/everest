from functools import wraps
from contextlib import contextmanager
import weakref
from collections import OrderedDict

from . import Built
from ._producer import Producer, Outs
from ._observable import Observable

from ..utilities import Grouper

from ..exceptions import *
class ObserverError(EverestException):
    '''An error has emerged related to the Observer class.'''
class ObserverInputError(ObserverError):
    '''Observer subjects must be instances of Observable class.'''
class ObserverMissingAsset(ObserverError, MissingAsset):
    pass
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
        self.constructs = weakref.WeakKeyDictionary()

        super().__init__(**kwargs)

    @_unattached
    def attach(self, subject):
        self.register(subject, silent = True)
        self.subject = subject
        self.subject._observer = self
    @_attached
    def detach(self, subject):
        self.subject._observer = None
        self.subject = None

    @contextmanager
    def observe(self, subject):
        self.attach(subject)
        try:
            yield
        finally:
            self.detach(subject)
    def __call__(self, subject):
        return self.observe(subject)

    def register(self, subject, silent = False):
        if not isinstance(subject, Observable):
            raise TypeError(
                "Observee must be an instance of the Observable class."
                )
        if not self in subject.observers:
            subject.observers.append(self)
        else:
            if not silent:
                raise ObserverError("Observer already registered.")
    def deregister(self, subject):
        if not isinstance(subject, Observable):
            raise TypeError(
                "Observee must be an instance of the Observable class."
                )
        if self in subject.observers:
            subject.observers.remove(self)
        else:
            if not silent:
                raise ObserverError("Observer not registered.")

    @_attached
    def evaluate(self):
        return self.construct.evaluate()

    @_attached
    def _obs_save(self):
        self.subject.writeouts.add(self, 'observer')

    @property
    @_attached
    def construct(self):
        if self.subject in self.constructs:
            construct = self.constructs[self.subject]
        else:
            construct = self.observer_construct(self.subject)
            self.constructs[self.subject] = construct
        return construct

    def observer_construct(self, subject):
        observer = self._observer_construct(subject, self.inputs)
        if not 'evaluate' in observer:
            raise ObserverMissingAsset
        return observer
    def _observer_construct(self, observables, inputs):
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
