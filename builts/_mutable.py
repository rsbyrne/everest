from collections import OrderedDict

from . import Built

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
class MutableException(BuiltException):
    pass
class MutableMissingMethod(MissingMethod, MutableException):
    pass
class MutableMissingAttribute(MissingAttribute, MutableException):
    pass
class MutableMissingKwarg(MissingKwarg, MutableException):
    pass

class Mutable(Built):

    def __init__(self,
            _mutableKeys = None,
            **kwargs
            ):

        if _mutableKeys is None:
            raise MutableMissingKwarg

        self.mutables = OrderedDict([(k, None) for k in _mutableKeys])

        super().__init__(**kwargs)
