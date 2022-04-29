###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import caching as _caching

from everest.ur import Dat as _Dat
from everest.primitive import Primitive as _Primitive

from .ousia import Ousia as _Ousia


class Atlantean(_Ousia):
    ...


@_Dat.register
class AtlanteanBase(metaclass=Atlantean):

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.make_epitaph()


###############################################################################
###############################################################################
