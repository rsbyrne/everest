from .._inquirer import Inquirer

class State(Inquirer):
    def __init__(
            self,
            evaluateFn,
            **kwargs
            ):
        super().__init__(
            _inquirer_meta_fn = all,
            **kwargs
            )
        self._inquirer_fns.append(evaluateFn)
