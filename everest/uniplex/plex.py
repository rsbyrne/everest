###############################################################################
''''''
###############################################################################


import os as _os
import weakref as _weakref

from everest.utilities import caching as _caching
from everest.utilities.file import H5File as _H5File

from everest.ptolemaic.sprite import Sprite as _Sprite

from everest.uniplex.folio import FolioLike as _FolioLike


class PlexFile(_H5File):

    DEFAULTEXT = 'plex'


class Plex(_FolioLike, metaclass=_Sprite):

    _req_slots__ = ('filepath',)

    name: str
    path: str = '~/'

    def __init__(self, /):
        super().__init__()
        self.filepath = PlexFile.get_filepath(self.name, self.path)

    # @_caching.weak_cache()
    def open_file(self, /):
        return PlexFile(self.filepath)

    @property
    def plex(self, /):
        return self

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        self.subs._repr_pretty_(p, cycle, root=root)


GLOBALPLEX = Plex('default')


###############################################################################
###############################################################################
