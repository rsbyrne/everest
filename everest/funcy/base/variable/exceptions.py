################################################################################

from ..exceptions import *

class VariableException(BaseException):
    pass

class VariableConstructFailure(BaseConstructFailure, VariableException):
    pass

################################################################################
