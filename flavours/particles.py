from ptolemaic import inner_class
from datalike.datums.numerical.vector import Position

from .base import Flavour
from ..frames._traversable import Traversable
from ..frames._chronable import Chronable

bases = Flavour, Traversable, Chronable
class Particles(*bases):

    @inner_class(*bases)
    class StateVar(Position):
        ...
