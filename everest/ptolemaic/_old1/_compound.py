###############################################################################
''''''
###############################################################################


from .ousia import Ousia as _Ousia
from .pentheros import Pentheros as _Pentheros


class Compound(_Pentheros, _Ousia):

    ...


class CompoundBase(metaclass=Compound):

    ...


###############################################################################
###############################################################################