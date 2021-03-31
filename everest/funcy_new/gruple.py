###############################################################################
'''Defines the 'gruple' types, which are incisable containers.'''
###############################################################################

from collections.abc import (
    Sequence as _Sequence,
    Iterable as _Iterable,
    Mapping as _Mapping,
    )
import operator as _operator

from .incision import (
    FuncySoftIncisable as _FuncySoftIncisable,
    FuncySoftIncision as _FuncySoftIncision,
    )
from . import abstract as _abstract
from .utilities import unpacker_zip as _unpacker_zip

def strict_expose(ind, self):
    return self(ind)

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

class _Gruple(_FuncySoftIncisable, _Sequence):

    pytype = list
    pylike = None

    @property
    def incisiontypes(self):
        return {
            **super().incisiontypes,
            'strict': strict_expose,
            'soft': self._swathetype
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
        return cls(boolzip)
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
        return f'{type(self).__name__}{str(self)}'
    def __str__(self):
        if len(self) < 10:
            return str(self.pytype(self))
        return f"[{str(self[:3])[1:-1]} ... {self.endval}]"

class Gruple(_Gruple):
    def __init__(self, arg: _Iterable, *args, lev = None, **kwargs):
        self.pylike = self.pytype(arg)
        if lev is None:
            lev = len(self.pylike)
        super().__init__(*args, lev = lev, **kwargs)
    def __call__(self, arg0, /, *argn):
        out = self.pylike[arg0]
        for arg in argn:
            out = out[arg]
        return out

class GrupleSwathe(_FuncySoftIncision, _Gruple):
    @property
    def pylike(self):
        return self.source.pylike
    def __repr__(self):
        return f'{repr(self.source)}[{repr(self.incisor)}]'

class _GrupleMap(_Gruple, _Mapping):
    pytype = dict
    @property
    def _swathetype(self):
        return GrupleMapSwathe
    def __iter__(self):
        return self.indices()
    @classmethod
    def rich(cls, self, other, /, *, opkey: str) -> 'GrupleMap':
        keys = self.pylike.keys()
        values = self.pylike.values()
        if isinstance(other, _Mapping):
            keys = Gruple(k for k in keys if k in other)
            other = Gruple(other[k] for k in keys)
        vals = Gruple.rich(values, other, opkey = opkey)
        return cls(zip(keys, vals))
    def __str__(self):
        if len(self) < 10:
            return str(self.pytype(zip(self.indices(), list(self))))
        initial = str(self[:3])[1:-1]
        final = f"{repr(self.endind[0])}: {repr(self.endval)}"
        return '{' + f"{initial} ... {final}" + '}'

class GrupleMap(_GrupleMap, Gruple):
    def index_sets(self):
        yield iter(self.pylike)
        yield from super().index_sets()
    def index_types(self):
        yield object
        yield from super().index_types()

class GrupleMapSwathe(_GrupleMap, GrupleSwathe):
    ...

###############################################################################
###############################################################################
