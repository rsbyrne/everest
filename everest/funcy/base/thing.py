################################################################################

from .base import Base as _Base

from .exceptions import *

class Thing(_Base):
    def __init__(self, thing, /, **kwargs):
        self.thing = thing
        super().__init__(**kwargs)
    def evaluate(self):
        return self.thing

################################################################################
