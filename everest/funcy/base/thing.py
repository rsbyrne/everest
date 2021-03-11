################################################################################

from .base import Base as _Base

from .exceptions import *

class Thing(_Base):
    __slots__ = ('_thing',)
    def __init__(self, thing, /, **kwargs):
        self._thing = thing
        super().__init__(**kwargs)
    @property
    def value(self):
        return self._thing

################################################################################