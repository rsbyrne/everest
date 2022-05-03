###############################################################################
''''''
###############################################################################


from .protean import Protean as _Protean
from .pentheros import Pentheros as _Pentheros


class Crucible(_Pentheros, _Protean):
    ...


class CrucibleBase(metaclass=Crucible):

    def __getstate__(self, /):
        return self.value

    @property
    def value(self, /):
        return self.__getstate__()

    def __setstate__(self, state, /):
        raise NotImplementedError

    def __reduce__(self, /):
        return (*super().__reduce__(), self.__getstate__())


###############################################################################
###############################################################################
