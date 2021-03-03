################################################################################

from .exceptions import *

from . import _Base

class Dat(_Base):
    def __init__(self,
            name: str,
            shape: tuple,
            ) -> None:
        super().__init__(
            name = name,
            shape = shape
            )
        self.shape = shape
    def evaluate(self):
        raise MissingAsset

################################################################################