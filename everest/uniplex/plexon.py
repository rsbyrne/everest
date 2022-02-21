###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.diict import Namespace as _Namespace
from everest.ptolemaic.ousia import Ousia as _Ousia

from .utilities import Attrs as _Attrs


class Plexon(metaclass=_Ousia):

    _req_slots__ = ('_attrs_',)

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._attrs_ = _Attrs()

    @property
    def attrs(self, /):
        return self._attrs_

    def __getitem__(self, name, /):
        return self.attrs[name]

    def __setitem__(self, name, val, /):
        if isinstance(val, _Primitive):
            self.attrs[name] = val
        else:
            raise TypeError(type(val))

    def __delitem__(self, name, /):
        del self.attrs[name]


class SubPlexon(Plexon):

    _req_slots__ = ('parent',)

    def __init__(self, /, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent

    @property
    def plex(self, /):
        return self.parent.plex


class GroupPlexon(Plexon, _Namespace):

    @property
    @_abc.abstractmethod
    def _defaultsub(self, /):
        raise NotImplementedError

    def sub(self, name, /, *args, typ=None, **kwargs):
        if typ is None:
            typ = self._defaultsub
        new = typ(self, *args, **kwargs)
        _Namespace.__setitem__(self, name, new)
        return new

    def __getitem__(self, key, /):
        try:
            return super().__getitem__(key)
        except KeyError:
            try:
                return _Namespace.__getitem__(self, key)
            except KeyError:
                return self.sub(key)

    def __delitem__(self, key, /):
        try:
            super().__delitem__(key)
        except KeyError:
            _Namespace.__delitem__(self, key)


###############################################################################
###############################################################################
