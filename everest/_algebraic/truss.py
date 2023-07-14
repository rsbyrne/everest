###############################################################################
''''''
###############################################################################


import itertools as _itertools

from everest.utilities import caching as _caching

from everest.ptolemaic.essence import Essence as _Essence

from everest.algebraic.brace import Brace as _Brace


class Truss(_Brace):

    class Oid(metaclass=_Essence):

        class Symmetric(metaclass=_Essence):

            @property
            @_caching.soft_cache()
            def shape(self, /):
                return tuple(_itertools.repeat(self.chora.depth, self.depth))

        class Asymmetric(metaclass=_Essence):

            @property
            @_caching.soft_cache()
            def shape(self, /):
                return tuple(chora.shape for chora in self.choras)

    @property
    @_caching.soft_cache()
    def shape(self, /):
        return tuple(member.shape for member in self)


###############################################################################
###############################################################################
