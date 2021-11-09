###############################################################################
''''''
###############################################################################


from everest.utilities import caching as _caching, word as _word
from everest.ptolemaic.metas.ousia import Ousia as _Ousia
from everest.ptolemaic.shades.shade import Shade as _Shade


class Hypostasis(_Shade, metaclass=_Ousia):
    '''
    The base class of all Ptolemaic types that can be instantiated.
    '''

    def _get_hashcode(self, /):
        raise NotImplementedError

    @property
    @_caching.soft_cache()
    def hashcode(self):
        return self._get_hashcode()

    @property
    @_caching.soft_cache()
    def hashint(self):
        return int(self.hashcode, 16)

    @property
    @_caching.soft_cache()
    def hashID(self):
        return _word.get_random_english(seed=self.hashint, n=2)

    def _repr(self, /):
        raise NotImplementedError

    @_caching.soft_cache()
    def __repr__(self, /):
        return f"<{repr(type(self))}({self._repr()})>"


###############################################################################
###############################################################################
