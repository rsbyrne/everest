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
class RequestAlreadyFiled(ObserverError):
    '''
    That request has already been filed. \
    Silence this error with the 'silent' keyword.
    '''
class RequestNotFiled(ObserverError):
    '''
    That request does not appear to have been filed. \
    Silence this error with the 'silent' keyword.
    '''
class PrompterNotFound(ObserverError):
    '''
    That prompter does not appear to have been registered \
    with the Observer. Use the 'request' method.
    '''

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
        # self._make_observer

        self.subject = None
        self.observer = None
        self._observers = weakref.WeakKeyDictionary()
        self._requests = weakref.WeakKeyDictionary()

        super().__init__(**kwargs)

        # Producer attributes:
        self._outFns.append(self._master_observer_out)

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
                observer = self.make_observer(subject.observables)
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

    def request(self, prompter, condition, silent = False):
        if not prompter in self._requests:
            self._requests[prompter] = []
        conditions = self._requests[prompter]
        if condition in conditions and not silent:
            raise RequestAlreadyFiled
        conditions.append(condition)
    def unrequest(self, prompter, condition, silent = False):
        try:
            conditions = self._requests[prompter]
            conditions.remove(condition)
        except (KeyError, ValueError):
            if not silent:
                raise RequestNotFiled
    def prompt(self, prompter):
        if not prompter in self._requests:
            raise PrompterNotFound
        conditions = self._requests[prompter]
        if any(conditions):
            with self.attach(prompter):
                self.store()

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

    def make_observer(self, observables):
        observerDict = self._make_observer(observables)
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
