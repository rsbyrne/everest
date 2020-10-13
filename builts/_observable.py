from contextlib import contextmanager

from ._mutable import Mutable
from ._producer import Producer
from ..weaklist import WeakList
from ..utilities import Grouper

class Observable(Producer, Mutable):

    def __init__(self,
            **kwargs
            ):

        self.observables = Grouper({})

        super().__init__(**kwargs)
