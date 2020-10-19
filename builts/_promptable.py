from . import Built
from ..exceptions import *

class Promptable(Built):

    def __init__(self,
            **kwargs
            ):

        super().__init__(**kwargs)

    def prompt(self):
        self._prompt()
    def _prompt(self):
        pass
