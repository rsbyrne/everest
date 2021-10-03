###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from . import _Ptolemaic
from . import _shades


class Schema(_shades.Singleton, _Ptolemaic):

    fixedsubclasses = ('Mapp', 'Brace', 'Slyce')

    Mapp = _shades.DictLike
    Brace = _shades.TupleLike
    Slyce = _shades.SliceLike

    @classmethod
    def yield_checktypes(cls, /):
        yield from super().yield_checktypes()
        yield _collabc.Mapping, lambda x: cls.Mapp(x)
        yield _collabc.Sequence, lambda x: cls.Brace(x)
        yield slice, lambda x: cls.Slyce(x)

    @classmethod
    def prekey(cls, params):
        return params.hashID

    def _repr(self):
        return self.params.hashID

    @property
    def hashID(self):
        return self._repr()


###############################################################################
###############################################################################
