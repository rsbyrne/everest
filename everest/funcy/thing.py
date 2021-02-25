################################################################################

from .basevar import Base
from .exceptions import *

class Thing(Base):
    def __init__(self, arg, **kwargs):
        super().__init__(arg, **kwargs)
    def evaluate(self):
        return self.prime

################################################################################
