###############################################################################
''''''
###############################################################################


from everest.utilities import caching as _caching, word as _word
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.aspect import Aspect as _Aspect


class Ptolemaic(_Aspect, metaclass=_Ousia):
    '''
    The base class of all Ptolemaic types that can be instantiated.
    '''

    def _repr(self, /):
        return ''

    @_caching.soft_cache()
    def __repr__(self, /):
        content = f"({rep})" if (rep := self._repr()) else ''
        return f"<{repr(type(self))}{content}>"

    def _get_hashcode(self, /):
        return self._repr()

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


###############################################################################
###############################################################################
