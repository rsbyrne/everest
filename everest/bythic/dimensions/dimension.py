###############################################################################
''''''
###############################################################################

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import abc as _collabc
import operator as _operator
from itertools import repeat as _repeat
from functools import partial as _partial, lru_cache as _lru_cache

from . import _special, _wordhash, _mroclasses

from . import _everestutilities
_ARITHMOPS = _everestutilities.ARITHMOPS
_RICHOPS = _everestutilities.RICHOPS
_REVOPS = _everestutilities.REVOPS
OPS = (*_ARITHMOPS, *_RICHOPS, *_REVOPS)

from .exceptions import (
    NotYetImplemented, DimensionUniterable, DimensionInfinite
    )

def unpack_slice(slc):
    return (slc.start, slc.stop, slc.step)

default_operator = lambda x: x


class DimIterator(_collabc.Iterator):

    __slots__ = ('gen',)

    def __init__(self, iter_fn, /):
        self.gen = iter_fn()
        super().__init__()

    def __next__(self):
        return next(self.gen)

    def __repr__(self):
        return f"{__class__.__name__}({repr(self.gen)})"


def calculate_len(dim):
    raise NotYetImplemented

def raise_uniterable():
    raise DimensionUniterable


class DimensionMeta(_ABCMeta):
    _DimIterator, _Derived, _Transform, _Slice = None, None, None, None
    @property
    def DimIterator(cls):
        if (icls := cls._DimIterator) is None:
            icls = type()


@_wordhash.Hashclass
@_mroclasses.MROClassable
class Dimension(metaclass = DimensionMeta):

    __slots__ = (
        '_args', '_kwargs', 'iterlen', 'iter_fn',
        'source', '_sourceget_', # required by Derived
        )
    mroclasses = ('_DimIterator', '_Derived', '_Transform', '_Slice')

    _DimIterator = DimIterator

    @_mroclasses.Overclass
    class _Derived:
        fixedoverclass = None
        def __init__(self, *sources):
            if not hasattr(self, '_args'):
                self._args = list()
            if not hasattr(self, '_kwargs'):
                self._kwargs = dict()
            source = None
            for source in sources:
                if isinstance(source, Dimension):
                    break
            if source is None:
                raise TypeError(
                    f"Source must be Dimension type, not {type(source)}"
                    )
            self.source = source
            if hasattr(source, '_sourceget_'):
                self._sourceget_ = source._sourceget_
            else:
                self._sourceget_ = type(source).__getitem__
            if not hasattr(self, 'iterlen'):
                self.iterlen = source.iterlen
            super().__init__()
            self._args.extend(sources)

        def __getitem__(self, arg):
            return self._sourceget_(self, arg)

    class _Transform(_Derived):

        def __init__(self, *operands, operator = default_operator):
            if isinstance(operator, str):
                if operator in OPS:
                    if operator in _REVOPS:
                        operator = operator[1:]
                        operands = operands[::-1]
                    operator = getattr(_operator, f"__{operator}__")
                else:
                    raise KeyError(operator)
            self.operands, self.operator = operands, operator
            if all(isinstance(op, Dimension) for op in operands):
                self.iter_fn = _partial(map, operator, *operands)
            else:
                getops = lambda: (
                    op if isinstance(op, Dimension) else _repeat(op)
                        for op in operands
                    )
                self.iter_fn = _partial(map, operator, *getops())
            super().__init__(*operands)
            self._kwargs['operator'] = operator

    class _Slice(_Derived):
        def __init__(self, source, incisor, /):
            super().__init__(source)
            self._args.append(incisor)

    DimIterator, Derived, Transform, Slice = object, object, object, object

    def __init__(self):
        if not hasattr(self, 'iterlen'):
            self.iterlen = None
        if not hasattr(self, 'iter_fn'):
            self.iter_fn = raise_uniterable
        self._args = []
        self._kwargs = dict()

    @property
    def args(self):
        return tuple(self._args)
    @property
    def kwargs(self):
        return tuple(self._kwargs.items())

    def __iter__(self):
        return DimIterator(self.iter_fn)

    def __len__(self):
        iterlen = self.iterlen
        if iterlen is None:
            self.iterlen = calculate_len(self)
            return self.__len__()
        if isinstance(iterlen, _special.InfiniteInteger):
            raise DimensionInfinite
        return iterlen

    def __bool__(self):
        iterlen = self.iterlen
        if iterlen is None:
            iterlen = self.iterlen = calculate_len(self)
        return iterlen > 0

    def __reduce__(self):
        return self._unreduce, (self.args, self.kwargs)

    @classmethod
    def _unreduce(cls, args, kwargs):
        return cls(*args, **dict(kwargs))

    def copy(self):
        return self._unreduce(self.args, self.kwargs)

    def get_hashcontents(self):
        return (type(self), self.args, self.kwargs)

    def transform(self, func):
        return _partial(self.Transform, operator = func)
    def apply(self, func):
        return self.transform(func)(self)

    @classmethod
    @_lru_cache(maxsize = 32)
    def _getop(cls, name, *args):
        if not (name := name.strip('_')) in OPS:
            raise KeyError
        return _partial(cls.Transform, *args, operator = name)
    def __getattr__(self, name):
        try:
            return self._getop(name, self)
        except KeyError as exc:
            raise AttributeError from exc

    @_abstractmethod
    def __getitem__(self, arg):
        '''This class wouldn't be of much use without one of these!'''

Derived = Dimension.Derived


class Tandem(Dimension):

    __slots__ = ('metrics',)

    def __init__(self, *args):
        metrics = []
        for arg in args:
            if isinstance(arg, tuple):
                metrics.extend(arg)
            elif isinstance(arg, Dimension):
                metrics.append(arg)
            else:
                raise TypeError(type(arg))
        metrics = self.metrics = tuple(metrics)
        self.iterlen = min(len(met) for met in metrics)
        self.iter_fn = lambda: zip(*self.metrics)
        self._args.extend(metrics)
        super().__init__()


###############################################################################
###############################################################################
