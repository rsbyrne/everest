################################################################################

from . import _Base

from .exceptions import *

class Dat(_Base):
    __slots__ = ('shape')
    def __init__(self, name: str, shape: tuple) -> None:
        super().__init__(name = name, shape = shape)
        self.shape = shape
    def evaluate(self):
        raise MissingAsset
    def __getitem__(self, arg):
        raise TypeError

################################################################################