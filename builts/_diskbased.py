from . import Built
from . import GLOBALANCHOR

class DiskBased(Built):

    def _post_build(self):
        # overrides post build method to ensure anchoring at init:
        global GLOBALANCHOR
        if GLOBALANCHOR: self.anchor()
        else: self.anchor(self.name, self.path)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
