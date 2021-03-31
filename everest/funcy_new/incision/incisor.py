###############################################################################
'''The module defining the top-level 'incisor' types.'''
###############################################################################

from . import _abstract
_FuncyABC = _abstract.abstract.FuncyABC
_datalike = _abstract.datalike
_general = _abstract.general
_structures = _abstract.structures

class FuncyIncisor(_FuncyABC):
    ...

class FuncyTrivialIncisor(FuncyIncisor):
    def __repr__(self):
        return 'trivial'
trivial = FuncyTrivialIncisor()

class FuncyShallowIncisor(FuncyIncisor):
    ...

class FuncyStrictIncisor(FuncyShallowIncisor):
    ...
_ = FuncyStrictIncisor.register(_datalike.FuncyIntegral)
_ = FuncyStrictIncisor.register(_datalike.FuncyString)
_ = FuncyStrictIncisor.register(_datalike.FuncyMapping)

class FuncySoftIncisor(FuncyShallowIncisor):
    ...
_ = FuncySoftIncisor.register(_general.FuncySlice)

class FuncyBroadIncisor(FuncySoftIncisor):
    ...
_ = FuncyBroadIncisor.register(_structures.FuncyUnpackable)

class FuncyDeepIncisor(FuncyIncisor):
    ...
_ = FuncyDeepIncisor.register(_structures.FuncyStruct)
_ = FuncyDeepIncisor.register(type(Ellipsis))

class FuncySubIncisor(FuncyDeepIncisor):
    ...
subinc = FuncySubIncisor()

###############################################################################
###############################################################################
