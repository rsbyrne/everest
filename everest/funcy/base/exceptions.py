################################################################################

from ..exceptions import *

class BaseException(FuncyException):
    ...

class BaseConstructFailure(ConstructFailure, BaseException):
    ...

################################################################################