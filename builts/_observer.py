from functools import wraps

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

@_attached
def _changed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.observed == self.subject.observables:
            self._master_observer_initialise()
        return func(self, *args, **kwargs)
    return wrapper

class Observer(Producer):

    def __init__(self,
            **kwargs
            ):

        # Expects:
        # self._observer_attach

        self.detach(silent = True)

        self.requests = dict()

        super().__init__(**kwargs)

        # Producer attributes:
        self._outFns.append(self._master_observer_out)

    def observe(self, subject):
        try:
            self.attach(subject)
        except AlreadyAttachedError:
            pass
        self.store()

    @_attached
    def detach(self):
        self.subject = None
        self.locals = None
        self._observer_out = None
        self.observed = None
        if isinstance(self.subject, Producer):
            self.subject._post_store_fns.remove(self.store)
            self.subject._post_anchor_fns.remove(self._anchor_to_subject)
            self.subject._post_save_fns.remove(self.save)

    def attach(self, subject):
        if self.subject is subject:
            raise AlreadyAttachedError
        if not isinstance(subject, Observable):
            raise ObserverInputError
        if not len(subject.observables):
            raise NoObservables
        self.subject = subject
        if isinstance(self.subject, Producer):
            self.subject._post_store_fns.append(self.store)
            self.subject._post_anchor_fns.append(self._anchor_to_subject)
            self.subject._post_save_fns.append(self.save)

    def _anchor_to_subject(self):
        self.anchor(self.subject.name, self.subject.path)

    @_changed
    def _master_observer_out(self):
        if isinstance(self.subject, Counter):
            for item in self.subject._countoutFn:
                yield item
        for item in self._observer_out():
            yield item

    @_attached
    def _master_observer_initialise(self):
        self.observed = self.subject.observables.copy()
        outFn, localsDict = self._attach(Grouper(self.observed))
        self.locals = Grouper(localsDict)
        delattr(locals, 'self')
        self._observer_out = outFn

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
