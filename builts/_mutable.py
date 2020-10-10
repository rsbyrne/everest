from collections import OrderedDict

from . import Built
from ..pyklet import Pyklet
from ..utilities import make_hash
from ..prop import Prop

from . import BuiltException, MissingMethod, MissingAttribute, MissingKwarg
class MutableException(BuiltException):
    pass
class MutableMissingMethod(MissingMethod, MutableException):
    pass
class MutableMissingAttribute(MissingAttribute, MutableException):
    pass
class MutableMissingKwarg(MissingKwarg, MutableException):
    pass

class Mutant(Pyklet):
    def __init__(self, target, *props):
        self.prop = Prop(target, *props)
        super().__init__(target, *props)
    def _hashID(self):
        return self.prop.hashID
    @property
    def var(self):
        return self.prop()
    @property
    def varHash(self):
        return make_hash(self.data)
    @property
    def data(self):
        return self._data()
    def mutate(self, data):
        return self._mutate(data)
    def imitate(self, fromVar):
        return self._imitate(fromVar)

class Mutable(Built):

    def __init__(self,
            _mutableKeys = None,
            **kwargs
            ):

        if _mutableKeys is None:
            raise MutableMissingKwarg

        self.mutables = OrderedDict([(k, None) for k in _mutableKeys])

        super().__init__(**kwargs)
