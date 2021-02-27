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

################################################################################
