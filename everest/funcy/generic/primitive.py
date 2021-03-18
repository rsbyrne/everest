################################################################################

from abc import ABC as _ABC

PRIMITIVETYPES = set((
    int,
    float,
    complex,
    str,
    type(None),
    tuple,
    ))
class Primitive(_ABC):
    ...
for typ in PRIMITIVETYPES:
    _ = Primitive.register(typ)

################################################################################