import weakref

from . import Built
from ..weaklist import WeakList
from ..exceptions import EverestException

class PromptableError(EverestException):
    '''
    Something went wrong in the Promptable class.
    '''
class RequestAlreadyFiled(PromptableError):
    '''
    That request has already been filed. \
    Silence this error with the 'silent' keyword.
    '''
class RequestNotFiled(PromptableError):
    '''
    That request does not appear to have been filed. \
    Silence this error with the 'silent' keyword.
    '''
class PrompterNotFound(PromptableError):
    '''
    That prompter does not appear to have been registered \
    with the Observer. Use the 'request' method.
    '''
class WrongRequestsChannel(PromptableError):
    '''
    The prompter could not be found in the requests dictionary; \
    either a request was never made, or it was made under a different key.
    '''

class Promptable(Built):

    _promptableDefaultKey = 'default'

    def __init__(self,
            **kwargs
            ):

        self._requests = dict()
        # {
        #     weakref.WeakKeyDictionary()

        self._pre_prompt_fns = WeakList()
        self._prompt_fns = WeakList()
        self._post_prompt_fns = WeakList()

        super().__init__(**kwargs)

    @property
    def _promptableKey(self):
        return self._promptableDefaultKey

    def request(self, prompter, condition, silent = False):
        requests = self._get_requests(make = True)
        if not prompter in self._requests:
            requests[prompter] = []
        conditions = requests[prompter]
        if condition in conditions and not silent:
            raise RequestAlreadyFiled
        conditions.append(condition)

    def unrequest(self, prompter, condition, silent = False):
        requests = self._get_requests()
        try:
            conditions = requests[prompter]
            conditions.remove(condition)
        except (KeyError, ValueError):
            if not silent:
                raise RequestNotFiled

    def prompt(self, prompter):
        requests = self._get_requests()
        if not prompter in requests:
            raise PrompterNotFound
        conditions = requests[prompter]
        if any(conditions):
            self._prompt(prompter)

    def advertise(self):
        requests = self._get_requests(make = True)
        for prompter in requests:
            self.prompt(prompter)

    def _get_requests(self, make = False):
        key = self._promptableKey
        if not key in self._requests:
            if make:
                self._requests[key] = weakref.WeakKeyDictionary()
            else:
                raise WrongRequestsChannel
        return self._requests[key]

    def _prompt(self, prompter):
        for fn in self._pre_prompt_fns: fn(prompter)
        for fn in self._prompt_fns: fn(prompter)
        for fn in self._post_prompt_fns: fn(prompter)
