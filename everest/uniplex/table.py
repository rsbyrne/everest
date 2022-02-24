###############################################################################
''''''
###############################################################################


from collections import deque as _deque
import itertools as _itertools
import abc as _abc

import numpy as _np

from everest.utilities import pretty as _pretty, caching as _caching

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ousia import Ousia as _Ousia

from everest.algebraic.intt import Intt as _Intt
from everest.algebraic.chora import ChainChora as _ChainChora

from .plexon import (
    Plexon as _Plexon,
    SubPlexon as _SubPlexon,
    )


class TableLike(_SubPlexon):

    MERGETUPLES = ('_var_slots__',)

    _req_slots__ = (
        '_openslc', 'depth',
        'queue', 'append', 'extend', 'clear',
        '_shape', 'baseshape', 'opendims', 'appendaxis',
        )
    _var_slots__ = ('shape', '_shape')

    def __init__(self, /, parent, shape=(), *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        if isinstance(shape, tuple):
            if not shape:
                shape = (None,)
        else:
            shape = (shape,)
        baseshape = self.baseshape = shape
        shape = self._shape = \
            tuple(0 if dim is None else dim for dim in baseshape)
        depth = self.depth = len(shape)
        self._openslc = tuple(_itertools.repeat(slice(None), depth))
        opendims = self.opendims = tuple(
            i for i, val in enumerate(baseshape)
            if val is None
            )
        if opendims:
            self.appendaxis = opendims[0]
            queue = self.queue = _deque()
            self.append = queue.append
            self.extend = queue.extend
            self.clear = queue.clear

    @property
    def shape(self, /):
        return self._shape

    @shape.setter
    def shape(self, val, /):
        self._shape = val
        self._update_shape()

    def _update_shape(self, /):
        pass

    def _yield_reshape(self, dims, /):
        newdims = iter(dims)
        opendims = self.opendims
        for i, currentdim in enumerate(self.shape):
            if i in opendims:
                try:
                    yield next(newdims)
                except StopIteration:
                    break
            else:
                yield currentdim
        else:
            yield from newdims

    def resize(self, dim0, /, *dimn):
        self.shape = tuple(self._yield_reshape((dim0, *dimn)))

    def stack(self, content, /):
        try:
            axis = self.appendaxis
        except AttributeError:
            raise ValueError("Cannot extend fixed array.")
        length = len(content)
        if not length:
            return
        self.resize(length+self.shape[axis])
        indices = list(self._openslc)
        indices[axis] = slice(-length, None)
        self[tuple(indices)] = content
        return length

    def resolve(self, /):
        if self.stack(queue := self.queue):
            queue.clear()


class ArrayLike(metaclass=_Essence):

    @property
    @_abc.abstractmethod
    def data(self, /):
        raise NotImplementedError

    @property
    @_abc.abstractmethod
    def mask(self, /):
        raise NotImplementedError

    @property
    def dtype(self, /):
        return self.data.dtype

    def __setitem__(self, key, val, /):
        if isinstance(key, str):
            super().__setitem__(key, val)
        else:
            self.mask[key] = True
            self.data[key] = val

    def __delitem__(self, key, /):
        if isinstance(key, str):
            super().__delitem__(key)
        else:
            self.mask[indices] = False


class Table(_ChainChora, ArrayLike, TableLike, metaclass=_Ousia):


    MROCLASSES = ('Slyce',)
    _req_slots__ = ('_data', '_mask')

    def __init__(self, /, parent, shape=(), dtype=float, *args, **kwargs):
        super().__init__(parent, shape, *args, **kwargs)
        shape = self.shape
        self._data = _np.empty(shape, dtype)
        self._mask = _np.empty(shape, bool)

    @property
    def data(self, /):
        return self._data

    @property
    def mask(self, /):
        return self._mask

    def _update_shape(self, /):
        shape = self.shape
        self.data.resize(shape, refcheck=False)
        self.mask.resize(shape, refcheck=False)
        try:
            del self.softcache['__incision_manager__']
        except KeyError:
            pass

    @property
    @_caching.soft_cache()
    def __incision_manager__(self, /):
        return _Intt.Oid.Brace[
            tuple(slice(0, val) for val in self.shape)
            ]

    def __incise_slyce__(self, incisor, /):
        return self.Slyce(self, incisor)

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        root += f"(shape={self.shape}, dtype={self.dtype})"
        _pretty.pretty_array(self.data, p, cycle, root=root)


    class Slyce(ArrayLike, _ChainChora, metaclass=_Ousia):

        _req_slots__ = ('source', 'incisor')

        def __init__(self, /, source, incisor):
            super().__init__()
            self.source, self.incisor = source, incisor

        @property
        def __incision_manager__(self, /):
            return self.incisor

        @property
        def shape(self, /):
            return self.data.shape

        @property
        def dtype(self, /):
            return self.source.dtype

        @property
        @_caching.soft_cache()
        def data(self, /):
            return self.source.data.view()[self.incisor.arrayquery]

        @property
        @_caching.soft_cache()
        def mask(self, /):
            return self.source.mask.view()[self.incisor.arrayquery]

        def __incise_slyce__(self, incisor, /):
            return self._ptolemaic_class__(self.source, incisor)

        def _repr_pretty_(self, p, cycle, root=None):
            if root is None:
                root = self._ptolemaic_class__.__qualname__
            with p.group(4, root + '(', ')'):
                p.breakable()
                p.text(f"source = {repr(self.source)}")
                p.text(',')
                p.breakable()
                p.text("incisor = ")
                self.incisor._repr_pretty_(p, cycle)
                p.text(',')
                p.breakable()
                p.text("data = ")
                _pretty.pretty_array(self.data, p, cycle)
                p.breakable()


###############################################################################
###############################################################################
