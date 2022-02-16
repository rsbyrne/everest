###############################################################################
''''''
###############################################################################


from types import MappingProxyType as _MappingProxyType
import functools as _functools
import operator as _operator
from collections import deque as _deque
import itertools as _itertools
import abc as _abc

import numpy as _np

from everest.utilities import pretty as _pretty, caching as _caching

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.chora import (
    Choric as _Choric,
    ChainChora as _ChainChora,
    Basic as _Basic,
    )
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.fundaments.intt import Intt as _Intt
# from everest.ptolemaic.fundaments.index import Index as _Index


class Ephemera(metaclass=_Essence):

    _req_slots__ = ('_attrs', 'attrs')

    def __init__(self, /):
        super().__init__()
        attrs = self._attrs = {}
        self.attrs = _MappingProxyType(attrs)

    def __setattr__(self, name, val, /):
        try:
            super().__setattr__(name, val)
        except AttributeError:
            self._attrs[name] = val

    def __delattr__(self, name, /):
        try:
            super().__delattr__(name)
        except AttributeError:
            try:
                del self._attrs[name]
            except KeyError as exc:
                raise AttributeError from exc


class TableLike(metaclass=_Essence):

    @property
    @_abc.abstractmethod
    def data(self, /):
        raise NotImplementedError

    @property
    @_abc.abstractmethod
    def mask(self, /):
        raise NotImplementedError

    @property
    def shape(self, /):
        return self.data.shape

    @property
    def dtype(self, /):
        return self.data.dtype

    def __setitem__(self, indices, val, /):
        self.mask[indices] = True
        self.data[indices] = val

    def __delitem__(self, indices, /):
        self.mask[indices] = False


class Table(TableLike, _ChainChora, Ephemera, metaclass=_Protean):


    MROCLASSES = ('Basis', 'Slyce')
    _req_slots__ = (
        '_data', '_mask', '_opendims', '_nopendims', '_queue',
        '_openslc', '_appendaxis', 'depth', 'append', 'extend',
        )
    _var_slots__ = ()


    class Basis(metaclass=_Sprite):

        shape: tuple
        dtype: (type, str)


    class Slyce(TableLike, _ChainChora, metaclass=_Sprite):

        source: object
        incisor: object  #_Index

        @property
        def __incision_manager__(self, /):
            return self.incisor

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


    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return super().__class_call__(cls.Basis(*args, **kwargs))

    def __init__(self, /):
        baseshape = self.basis.shape
        shape = tuple(0 if dim is None else dim for dim in baseshape)
        depth = self.depth = len(shape)
        self._openslc = tuple(_itertools.repeat(slice(None), depth))
        self._data = _np.empty(shape, self.basis.dtype)
        self._mask = _np.empty(shape, bool)
        opendims = self._opendims = tuple(val is None for val in baseshape)
        self._nopendims = sum(opendims)
        try:
            self._appendaxis = opendims.index(True)
        except ValueError:
            pass
        else:
            queue = self._queue = _deque()
            self.append = queue.append
            self.extend = queue.extend

    @property
    def data(self, /):
        return self._data

    @property
    def mask(self, /):
        return self._mask

    def _yield_reshape(self, dims, /):
        dims = iter(dims)
        for dim in self.shape:
            if dim is None:
                yield next(dims)
            else:
                yield dim

    def resize(self, dim0, /, *dimn):
        dims = (dim0, *dimn)
        if len(dims) > self._nopendims:
            raise ValueError
        idims = iter(dims)
        shape = tuple(
            next(idims, dim) if dim is None else dim
            for dim in self.basis.shape
            )
        self.data.resize(shape, refcheck=False)
        self.mask.resize(shape, refcheck=False)

    def stack(self, content, /):
        length = len(content)
        if not length:
            return
        appendaxis = self._appendaxis
        indices = list(self._openslc)
        indices[appendaxis] = slice(-length, None)
        self.resize(length + self.shape[appendaxis])
        self[tuple(indices)] = content
        return length

    def resolve(self, /):
        if self.stack(queue := self._queue):
            queue.clear()

    @property
    @_caching.soft_cache()
    def __incision_manager__(self, /):
        return _Intt.Oid.Brace[
            tuple(slice(0, val) for val in self.basis.shape)
            ]

    def __incise_slyce__(self, incisor, /):
        return self.Slyce(self, incisor)

    def _repr_pretty_base(self, p, cycle):
        root = self._ptolemaic_class__.__qualname__
        p.text(root + '(')
        _pretty.pretty_array(self.data, p, cycle)
        p.text(')')


class Folio(_Choric, Ephemera, metaclass=_Ousia):

    _req_slots__ = (
        'content', '_content'
        )

    def __init__(self, /, **content):
        super().__init__()
        self._content = content
        self.content = _MappingProxyType(content)

    class __choret__(_Basic, metaclass=_Essence):

        def retrieve_tuple(self, incisor: tuple, /):
            out = self.bound.content
            for sub in incisor:
                out = out[sub]
            return out

        def retrieve_str(self, incisor: str, /):
            return self.bound.content[incisor]

        @property
        def __incise_contains__(self, /):
            return self.bound.content.__contains__

        @property
        def __incise_iter__(self, /):
            return self.bound.content.__iter__

        @property
        def __incise_len__(self, /):
            return self.bound.content.__len__

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self.content, p, cycle, root=root)


###############################################################################
###############################################################################
