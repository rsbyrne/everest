###############################################################################
'''Defines the 'gruple' types, which are incisable containers.'''
###############################################################################

from collections.abc import (
    Sequence as _Sequence,
    Iterable as _Iterable,
    Mapping as _Mapping,
    )
import operator as _operator

from . import abstract as _abstract
from .utilities import unpacker_zip as _unpacker_zip

def strict_expose(self, ind):
    return self.incision_finalise(ind)

def flatlen(gruple):
    _n = 0
    for _c in gruple.pylike:
        try:
            _n += _c.flatlen
        except AttributeError:
            if isinstance(_c, _abstract.FuncyUnpackable):
                _n += len(_c)
            else:
                _n += 1
    return _n

class _Gruple(_abstract.FuncySoftIncisable, _Sequence):

    pytype = list
    pylike = None

    @property
    def incisionTypes(self):
        return {
            **super().incisionTypes,
            'strict': strict_expose,
            'broad': self._swathetype
            }

    @property
    def _swathetype(self):
        return GrupleSwathe

    @property
    def flatlen(self):
        '''Returns the sum of the flatlengths of all unpackable contents.'''
        return flatlen(self)

    @classmethod
    def rich(cls, self, other, /, *, opkey: str) -> 'Gruple':
        opfn = getattr(_operator, opkey)
        boolzip = (opfn(s, o) for s, o in _unpacker_zip(self, other))
        return cls(boolzip, shape = self.shape)
    def __lt__(self, other):
        return self.rich(self, other, opkey = 'lt')
    def __le__(self, other):
        return self.rich(self, other, opkey = 'le')
    def __eq__(self, other):
        return self.rich(self, other, opkey = 'eq')
    def __ne__(self, other):
        return self.rich(self, other, opkey = 'ne')
    def __gt__(self, other):
        return self.rich(self, other, opkey = 'gt')
    def __ge__(self, other):
        return self.rich(self, other, opkey = 'ge')

    def __repr__(self):
        return f'{type(self).__name__}{self.pylike}'
    def __str__(self):
        if len(self) < 10:
            return str(self.pylike)
        return 'long'
        # return f"{self[:3]}

class Gruple(_Gruple):
    def __init__(self, arg: _Iterable, *args, **kwargs):
        self.pylike = self.pytype(arg)
        super().__init__(*args, shape = (len(self.pylike),), **kwargs)
    def incision_finalise(self, arg0, /):
        return self.pylike[arg0]

class GrupleSwathe(_abstract.FuncyBroadIncision, _Gruple):
    @property
    def pylike(self):
        return self.source.pylike
    def __repr__(self):
        return f'Swathe({repr(self.source)}[{repr(self.incisor)}])'
    def __str__(self):
        return str(self.pytype(self))

class _GrupleMap(_Gruple, _Mapping):
    pytype = dict
    @property
    def _swathetype(self):
        return GrupleMapSwathe
    @classmethod
    def rich(cls, self, other, /, *, opkey: str) -> 'GrupleMap':
        keys = self.pylike.keys()
        values = self.pylike.values()
        if isinstance(other, _Mapping):
            keys = Gruple(k for k in keys if k in other)
            other = Gruple(other[k] for k in keys)
        vals = Gruple.rich(values, other, opkey = opkey)
        return cls(zip(keys, vals), shape = self.shape)

class GrupleMap(_GrupleMap, Gruple):
    def index_sets(self):
        yield iter(self.pylike)
    def index_types(self):
        yield object

class GrupleMapSwathe(_GrupleMap, GrupleSwathe):
    ...

###############################################################################
###############################################################################
