###############################################################################
from . import Frame

class Promptable(Frame):

    def __init__(self,
            **kwargs
            ):

        super().__init__(**kwargs)

    def prompt(self):
        self._prompt()
    def _prompt(self):
        pass

###############################################################################
