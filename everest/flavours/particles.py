################################################################################
# from ..datalike.datums.numerical.vector import Position
from ..funcy.base.variable import Array

from .base import Flavour
from ..ptolemaic.frames import Traversable, Chronable

class Particles(Flavour, Traversable, Chronable):
    @classmethod
    def _stateVar_construct(cls):
        super()._stateVar_construct()
        class StateVar(cls.StateVar, Array):
            ...
        cls.StateVar = StateVar
        return

################################################################################
