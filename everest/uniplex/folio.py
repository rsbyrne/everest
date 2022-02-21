###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.diict import WeakNamespace as _WeakNamespace

from .plexon import GroupPlexon as _GroupPlexon, SubPlexon as _SubPlexon
from .table import (
    Table as _Table,
    MultiTable as _MultiTable,
    )


class FolioLike(_GroupPlexon, _WeakNamespace):

    def folio(self, /, *args, **kwargs):
        return self.sub(*args, typ=Folio, **kwargs)

    def table(self, /, *args, **kwargs):
        return self.sub(*args, typ=_Table, **kwargs)

    def multi(self, /, *args, **kwargs):
        return self.sub(*args, typ=_MultiTable, **kwargs)

    @property
    def _defaultsub(self, /):
        return Folio


class Folio(_SubPlexon, FolioLike):
    ...


###############################################################################
###############################################################################
