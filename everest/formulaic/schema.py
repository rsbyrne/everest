###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.sprite import Sprite as _Sprite

from everest.uniplex.plex import Plex as _Plex, GLOBALPLEX as _GLOBALPLEX


class Schema(_Sprite):

    ...


class SchemaBase(metaclass=_Sprite):

    _req_slots__ = ('_plex_',)
    _var_slots__ = ('plex',)

    def __init__(self, /):
        super().__init__()
        self._plex_ = _GLOBALPLEX

    @property
    def plex(self, /):
        return self._plex_

    @plex.setter
    def plex(self, val, /):
        self.mount_plex(val)

    def mount_plex(self, plex):
        with self.mutable:
            self._plex_ = val

    @property
    def folio(self, /):
        return self.plex[self.hashID]


###############################################################################
###############################################################################
