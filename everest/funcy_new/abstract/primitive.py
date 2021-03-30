###############################################################################
'''The module describing the 'primitive' types understood by funcy.'''
###############################################################################

from .abstract import FuncyABC as _FuncyABC

PRIMITIVETYPES = set((
    int,
    float,
    complex,
    str,
    type(None),
    tuple,
    ))

class FuncyPrimitive(_FuncyABC):
    '''The virtual superclass of all acceptable funcy primitive types.'''
for typ in PRIMITIVETYPES:
    _ = FuncyPrimitive.register(typ)

###############################################################################
###############################################################################
