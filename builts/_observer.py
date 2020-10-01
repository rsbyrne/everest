from functools import wraps
from contextlib import contextmanager
import weakref

from ._observable import Observable
from ._producer import Producer
from ._counter import Counter

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

class Observer(Producer):

    def __init__(self,
            **kwargs
            ):

        # Expects:
        # self.build_observer

        self.subject = None
        self.observer = None
        self._observers = weakref.WeakKeyDictionary()

        super().__init__(**kwargs)

        # Producer attributes:
        self._outFns.append(self._master_observer_out)
        self._producer_outkeys.append(self._observer_outkeys)

    @contextmanager
    @_unattached
    def attach(self, subject):
        try:
            wasAnchored = self.anchored
            if wasAnchored:
                wasName, wasPath = self.name, self.path
            try:
                observer = self._observers[self]
            except KeyError:
                observer = self.master_build_observer(subject.observables)
                self._observers[subject] = observer
            if isinstance(subject, Producer):
                subject._post_store_fns.append(self.store)
                subject._post_anchor_fns.append(self._anchor_to_subject)
                subject._post_save_fns.append(self.save)
            self.subject = subject
            self.observer = observer
            yield observer
        finally:
            if wasAnchored:
                self.anchor(wasName, wasPath)
            if isinstance(subject, Producer):
                subject._post_store_fns.remove(self.store)
                subject._post_anchor_fns.remove(self._anchor_to_subject)
                subject._post_save_fns.remove(self.save)
            self.subject = None
            self.observer = None

    @_attached
    def _anchor_to_subject(self):
        self.anchor(self.subject.name, self.subject.path)

    @_attached
    def _master_observer_out(self):
        if isinstance(self.subject, Counter):
            for item in self.subject._countoutFn():
                yield item
        for item in self.observer.out():
            yield item

    @_attached
    def _observer_outkeys(self):
        if isinstance(self.subject, Counter):
            for key in self.subject._countsKeyFn():
                yield key
        for key in self.observer.outkeys:
            yield key

    def master_build_observer(self, observables):
        observerDict = self.build_observer(observables)
        if 'self' in observerDict:
            del observerDict['self']
        return Grouper(observerDict)

    @property
    @_attached
    def _outputMasterKey(self):
        # Overrides Producer attribute
        if isinstance(self.subject, Producer):
            return self.subject._outputMasterKey
        else:
            return self.subject.hashID
    @property
    @_attached
    def _outputSubKey(self):
        # Overrides Producer attribute
        key = ''
        if isinstance(self.subject, Producer):
            key += self.subject._outputSubKey + '/'
        key += '/'.join(['observations', self.hashID])
        return key

    @_attached
    def store(self):
        # Overrides and calls Producer store method:
        super().store()
    @_attached
    def save(self):
        # Overrides and calls Producer save method:
        super().store()

    def _prompt(self, prompter):
        # Overrides Promptable _prompt method:
        if self.subject is None:
            with self.attach(prompter):
                super()._prompt(prompter)
        elif prompter is self.subject:
            super()._prompt(prompter)
        else:
            raise AlreadyAttachedError

    def _producer_post_anchor(self):
        # Wraps Producer method
        if not self.subject is None:
            super()._producer_post_anchor()
