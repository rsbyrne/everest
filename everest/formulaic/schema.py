###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import caching as _caching
from everest.bureau.bureau import open_drawer as _open_drawer
from everest.ptolemaic.compound import Compound as _Compound
from everest.algebraic.bythos import Bythos as _Bythos
from everest.uniplex.plex import Plex as _Plex, GLOBALPLEX as _GLOBALPLEX

from .formulaic import Formulaic as _Formulaic


class Schema(_Compound, _Bythos):

    @property
    @_caching.weak_cache()
    def drawer(cls, /):
        return _open_drawer(cls)


class SchemaBase(_Formulaic, metaclass=_Compound):

    @property
    @_caching.weak_cache()
    def drawer(cls, /):
        return _open_drawer(cls)


###############################################################################
###############################################################################


#     _req_slots__ = ('_plex_',)
#     _var_slots__ = ('plex',)

#     def __init__(self, /):
#         super().__init__()
#         self._plex_ = _GLOBALPLEX

#     @property
#     def plex(self, /):
#         return self._plex_

#     @plex.setter
#     def plex(self, val, /):
#         self.mount_plex(val)

#     def mount_plex(self, plex):
#         with self.mutable:
#             self._plex_ = val

#     @property
#     def plexon(self, /):
#         return self.plex.folio(self.hashID)
