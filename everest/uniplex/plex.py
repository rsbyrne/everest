###############################################################################
''''''
###############################################################################


import os as _os
import weakref as _weakref

from everest.ptolemaic.sprite import Sprite as _Sprite

from everest.uniplex.folio import FolioLike as _FolioLike
from everest.uniplex.table import Table as _Table


class Plex(_FolioLike):

    ext = 'plex'

    _req_slots__ = ('filename', 'filepath', 'path', 'name')

    def __init__(self, /, path: str = '~/', name: str = 'default'):
        super().__init__()
        self.path, self.name = path, name
        filename = self.filename = '.'.join((name, self.ext))
        self.filepath = _os.path.join(path, filename)

    @property
    def plex(self, /):
        return self


GLOBALPLEX = Plex()


###############################################################################
###############################################################################
