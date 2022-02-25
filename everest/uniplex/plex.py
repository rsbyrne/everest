###############################################################################
''''''
###############################################################################


import os as _os
import weakref as _weakref

from everest.utilities import caching as _caching
from everest.utilities.file import H5File as _H5File

from everest.ptolemaic.ousia import Ousia as _Ousia

from everest.uniplex.folio import FolioLike as _FolioLike


class PlexFile(_H5File):

    DEFAULTEXT = 'plex'


class Plex(_FolioLike, metaclass=_Ousia):

    _req_slots__ = ('name', 'path', 'filepath')

    def __init__(self, name: str, /, path: str = '~/'):
        super().__init__()
        self.name, self.path = name, path
        self.filepath = PlexFile.get_filepath(name, path)

    # @_caching.weak_cache()
    def open_file(self, /):
        return PlexFile(self.filepath)

    @property
    def plex(self, /):
        return self


GLOBALPLEX = Plex('default')


###############################################################################
###############################################################################
