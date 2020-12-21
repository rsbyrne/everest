from everest.ptolemaic import inner_class
from everest.datalike.datums.numerical.vector import Position

from .base import Flavour
from ..frames._traversable import Traversable
from ..frames._chronable import Chronable

class Particles(Flavour, Traversable, Chronable):

    @classmethod
    def _class_construct(cls):
        super()._class_construct()
        class StateVar(cls.StateVar, Position):
            ...
        cls.StateVar = StateVar
