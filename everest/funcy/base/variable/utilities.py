################################################################################

from .scalar import construct_scalar as _construct_scalar
from .array import construct_array as _construct_array
from .variable import Variable as _Variable

from .exceptions import *

def construct_variable(arg = None, /, *args, **kwargs) -> _Variable:
    es = []
    for meth in (_construct_scalar, _construct_array):
        try:
            return meth(arg, *args, **kwargs)
        except VariableConstructFailure as e:
            es.append(e)
    raise VariableConstructFailure(
        "Variable construct failed"
        f" with args = {(arg, *args)}, kwargs = {kwargs};"
        f" {tuple(es)}"
        )

################################################################################