################################################################################

from collections.abc import (
    Sequence as _Sequence,
    Iterable as _Iterable,
    Mapping as _Mapping,
    )
import operator as _operator

from . import generic as _generic
from .utilities import unpacker_zip as _unpacker_zip

def strict_expose(self, ind):
    return self._incision_finalise(ind)

class _Gruple(_generic.FuncySoftIncisable, _Sequence):
    @property
    def incisionTypes(self):
        return {
            **super().incisionTypes,
            'strict': strict_expose,
            'broad': GrupleSwathe,
            }
    @property
    def pyLike(self):
        return self._pyLike
    def _incision_finalise(self, arg0, /):
        return self.pyLike[arg0]
    @property
    def flatlen(self):
        try:
            return self._flatlen
        except AttributeError:
            n = 0
            for c in self.pyLike:
                try:
                    n += c.flatlen
                except AttributeError:
                    if isinstance(c, _generic.FuncyUnpackable):
                        n += len(c)
                    else:
                        n += 1
            self._flatlen = n
            return n
    @classmethod
    def _rich(cls, self, other, /, *, opkey: str) -> 'Gruple':
        opfn = getattr(_operator, opkey)
        boolzip = (opfn(s, o) for s, o in _unpacker_zip(self, other))
        return cls(boolzip)
    def __lt__(self, other): return self._rich(self, other, opkey = 'lt')
    def __le__(self, other): return self._rich(self, other, opkey = 'le')
    def __eq__(self, other): return self._rich(self, other, opkey = 'eq')
    def __ne__(self, other): return self._rich(self, other, opkey = 'ne')
    def __gt__(self, other): return self._rich(self, other, opkey = 'gt')
    def __ge__(self, other): return self._rich(self, other, opkey = 'ge')

class Gruple(_Gruple):
    def __init__(self, args: _Iterable, /):
        self._pyLike = list(args)
        super().__init__()
    @property
    def shape(self):
        return (len(self.pyLike),)
    def _index_sets(self):
        yield iter(self.pyLike)
    def _index_types(self):
        yield object
    def __repr__(self):
        return f'Gruple{self.pyLike}'
    def __str__(self):
        return self.__repr__()

class _GrupleSwathe(_Gruple, _generic.FuncyBroadIncision):
    @property
    def pyLike(self):
        return self.source.pyLike
    def __repr__(self):
        return f'Swath({repr(self.source)}[{repr(self.incisor)}])'
    def __str__(self):
        return str(list(self))

class GrupleSwathe(_GrupleSwathe):
    ...

class _GrupleMap(_Gruple, _Mapping):
    @property
    def incisionTypes(self):
        return {
            **super().incisionTypes,
            'broad': GrupleMapSwathe,
            }
    @classmethod
    def _rich(cls, self, other, /, *, opkey: str) -> 'GrupleMap':
        keys = self._keys
        if isinstance(other, _Mapping):
            keys = Gruple(k for k in keys if k in other)
            other = Gruple(other[k] for k in keys)
        vals = Gruple._rich(self._values, other, opkey = opkey)
        return cls(zip(keys, vals))

class GrupleMap(_GrupleMap):
    def __init__(self, pairs, /) -> None:
        self._pyLike = dict(pairs)
        super().__init__()
    @property
    def shape(self):
        return (len(self.pyLike),)
    def _index_sets(self):
        yield iter(self.pyLike)
    def _index_types(self):
        yield object
    def __repr__(self):
        return f'GrupleMap{self.pyLike}'

class GrupleMapSwathe(_GrupleMap, _GrupleSwathe):
    ...

################################################################################
