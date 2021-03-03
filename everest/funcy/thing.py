################################################################################

from .base import Base as _Base
from .exceptions import *

class Thing(_Base):
    def __init__(self, arg, **kwargs):
        super().__init__(arg, **kwargs)
    def evaluate(self):
        return self.prime

################################################################################
