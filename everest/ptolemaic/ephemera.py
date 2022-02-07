###############################################################################
''''''
###############################################################################


from types import MappingProxyType as _MappingProxyType
import functools as _functools
import operator as _operator
from collections import deque as _deque
import itertools as _itertools

import numpy as _np

from everest.incision import ChainIncisable as _ChainIncisable
from everest.utilities import pretty as _pretty, caching as _caching

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.protean import Protean as _Protean
from everest.ptolemaic.sprite import Sprite as _Sprite
from everest.ptolemaic.chora import Chora as _Chora, Basic as _Basic
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.eidos import Eidos as _Eidos
from everest.ptolemaic.fundaments.intt import Intt as _Intt


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


class Table(_ChainIncisable, Ephemera, metaclass=_Protean):


    MROCLASSES = ('Basis', 'Slyce')
    _req_slots__ = (
        '_array', '_mask', '_opendims', '_nopendims', '_queue',
        '_openslc', '_appendaxis', 'depth', 'append', 'extend',
        )
    _var_slots__ = ()

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return super().__class_call__(cls.Basis(*args, **kwargs))

    @property
    def shape(self, /):
        return self._array.shape

    @property
    def dtype(self, /):
        return self.basis.dtype

    def __init__(self, /):
        baseshape = self.basis.shape
        shape = tuple(0 if dim is None else dim for dim in baseshape)
        depth = self.depth = len(shape)
        self._openslc = tuple(_itertools.repeat(slice(None), depth))
        self._array = _np.empty(shape, self.dtype)
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
    def array(self, /):
        return self._array

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
        self._array.resize(shape, refcheck=False)
        self._mask.resize(shape, refcheck=False)

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
        return _Intt.Brace[tuple(slice(0, val) for val in self.basis.shape)]

    def __setitem__(self, indices, val, /):
        self._mask[indices] = True
        self._array[indices] = val

    def __delitem__(self, indices, /):
        self._mask[indices] = False

    def __incise_slyce__(self, incisor, /):
        return self.Slyce(self, incisor)


    class Basis(metaclass=_Sprite):

        shape: tuple
        dtype: (type, str)


    class Slyce(_ChainIncisable, metaclass=_Sprite):

        basis: object
        incisor: object

        _req_slots__ = ('__incision_manager__',)

        def __init__(self, /):
            self.__incision_manager__ = self.incisor

        @property
        def __incise_slyce__(self, /):
            return _functools.partial(self._ptolemaic_class__, self.basis)


    def _repr_pretty_base(self, p, cycle):
        _pretty.pretty_kwargs(self.basis.params, p, cycle, root=self.rootrepr)
        arraytext = _np.array2string(self._array, threshold=100)
        with p.group(4, '[', ']'):
            p.breakable()
            for row in arraytext[:-1].split('\n'):
                p.text(row[1:])
                p.breakable()


class Folio(_Chora, Ephemera, metaclass=_Ousia):

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

    def _repr_pretty_(self, p, cycle):
        root = ':'.join((
            self._ptolemaic_class__.__name__,
            str(id(self)),
            ))
        _pretty.pretty_kwargs(self.content, p, cycle, root=root)


###############################################################################
###############################################################################
