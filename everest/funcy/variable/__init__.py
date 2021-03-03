################################################################################

from ..function import Function as _Function
from ..base import Base as _Base
from ..map import Map as _Map
from .. import special as _special

from .variable import Variable
from .number import Number
from .scalar import Scalar
from .array import Array
from .stack import Stack
from .varmap import VarMap
from .exceptions import VariableException
from .utilities import construct_variable

Variable.construct_variable = construct_variable

################################################################################
