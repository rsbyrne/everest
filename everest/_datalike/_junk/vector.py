###############################################################################
from .spatial import Spatial, Linear, Planar, Volar

class Vector(Spatial):
    ...

class Scalito(Vector, Linear):
    ...

class Planito(Vector, Planar):
    ...

class Volito(Vector, Volar):
    ...

###############################################################################
