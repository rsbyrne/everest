################################################################################

from numbers import Number
from array import ArrayType

import numpy as np




PRIMITIVETYPES = set((
    Number,
    str,
    np.ndarray,
    ArrayType,
    type(None),
    tuple,
    ))



from abc import ABC



class FuncyNumerical(ABC):
    ...



class FuncyString(ABC):
    ...
_ = FuncyString.register(str)

class FuncyBool(ABC):
    ...
_ = FuncyBool.register(bool)

class FuncyArray(ABC):
    ...
_ = FuncyArray.register(np.ndarray)

class FuncyNoneType(ABC):
    ...
_ = FuncyNoneType.register(type(None))



from numbers import *

class FuncyNumber(ABC):
    ...
_ = FuncyNumber.register(Number)

class FuncyComplex(FuncyNumber):
    ...
_ = FuncyComplex.register(Complex)

class FuncyReal(FuncyComplex):
    ...
_ = FuncyReal.register(Real)

class FuncyRational(FuncyReal):
    ...
_ = FuncyRational.register(Rational)

class FuncyIntegral(FuncyRational):
    ...
_ = FuncyIntegral.register(Integral)



from collections.abc import *

class FuncyContainer(ABC):
    ...
_ = FuncyContainer.register(Container)

class FuncyIterable(ABC):
    ...
_ = FuncyIterable.register(Iterable)

class FuncySized(ABC):
    ...
_ = FuncySized.register(Sized)

class FuncyCallable(ABC):
    ...
_ = FuncyCallable.register(Callable)

class FuncyCollection(FuncySized, FuncyIterable, FuncyContainer):
    ...
_ = FuncyCollection.register(Collection)

class FuncyReversible(ABC):
    ...
_ = FuncyReversible.register(Reversible)

class FuncySequence(FuncyReversible, FuncyCollection):
    ...
_ = FuncySequence.register(Sequence)

class FuncyMapping(FuncyCollection):
    ...
_ = FuncyMapping.register(Mapping)

################################################################################
