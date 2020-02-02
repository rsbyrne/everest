from . import Built
from ..exceptions import EverestException

class InquirerError(EverestException):
    pass
class ArgTypeError(InquirerError):
    pass

class Inquirer(Built):
    def __init__(
            self,
            _inquirer_meta_fn = all,
            _inquirer_arg_typeCheck = lambda x: x,
            **kwargs
            ):
        self._pre_inquire_fns = []
        self._inquire_fns = []
        self._post_inquire_fns = []
        self._inquirer_meta_fn = _inquire_meta_fn
        self._inquirer_arg_typeCheck = _inquirer_arg_typeCheck
        super().__init__(**kwargs)
    def __call__(self, arg):
        if not self._inquirer_arg_typeCheck(arg):
            raise ArgTypeError
        for fn in self._pre_inquire_fns: fn()
        truths = [fn(arg) for fn in self._inquire_fns]
        truth = self._inquirer_meta_fn(truths)
        for fn in self._post_inquire_fns: fn()
        return truth
