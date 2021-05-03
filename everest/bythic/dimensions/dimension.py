###############################################################################
''''''
###############################################################################

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import abc as _collabc
from itertools import repeat as _repeat
from functools import partial as _partial

from . import _special, _classtools

from .exceptions import (
    DimensionUniterable, DimensionInfinite
    )


def calculate_len(dim):
    i = None
    for i, _ in enumerate(zip(dim, range(int(1e9)))):
        continue
    if i is None:
        return 0
    return i + 1

def raise_uniterable():
    raise DimensionUniterable

def show_iter_vals(iterable):
    i, ii = list(iterable[:6]), list(iterable[:7])
    content = ', '.join(str(v) for v in i)
    if len(ii) > len(i):
        content += ' ...'
    return f'[{content}]'


class DimensionMeta(_ABCMeta):
    ...

@_classtools.Diskable
@_classtools.MROClassable
@_classtools.Operable
class Dimension(metaclass = DimensionMeta):

    __slots__ = (
        '__dict__', 'iterlen', 'iter_fn', 'source', '_sourceget_',
        '_repr',
        )
    mroclasses = ('DimIterator', 'Derived', 'Transform', 'Slice')

    typ = None

    def __init__(self, typ = None):
        if not hasattr(self, 'iterlen'):
            self.iterlen = calculate_len(self)
        if not hasattr(self, 'iter_fn'):
            self.iter_fn = raise_uniterable
        if not typ is None:
            if not (styp := self.typ) is None:
                raise ValueError(
                    f"Multiple values interpreted for typ: {typ, styp}"
                    )
            self.typ = typ
        if self.typ is None:
            self.typ = object
        super().__init__()

    @property
    def tractable(self):
        return self.iterlen < _special.inf

    def count(self, value):
        if not self.tractable:
            raise ValueError("Cannot count occurrences in infinite iterator.")
        i = 0
        for val in self:
            if val == value:
                i += 1
        return i

    def _iter(self):
        return self.Iterator(self.iter_fn)
    def __iter__(self):
        return self._iter()

    def __len__(self):
        if isinstance(iterlen := self.iterlen, _special.InfiniteInteger):
            raise DimensionInfinite
        return iterlen

    @_abstractmethod
    def __getitem__(self, arg):
        '''This class wouldn't be of much use without one of these!'''

    def __bool__(self):
        return self.iterlen > 0

    def get_valstr(self):
        if self.iterlen <= 7:
            return str(list(self))[1:-1]
        start = str(list(self[:3]))[1:-1]
        if self.tractable:
            end = str(list(self[-2:]))[1:-1]
            return f"{start} ... {end}"
        return f"{start}"
    def get_repr(self):
        return f"{type(self).__name__} == [{self.get_valstr()}]"
    def __repr__(self):
        try:
            return self._repr
        except AttributeError:
            _repr = self._repr = self.get_repr() # pylint: disable=W0201
            return _repr

    class Iterator(_collabc.Iterator):
        __slots__ = ('gen',)
        def __init__(self, iter_fn, /):
            self.gen = iter_fn()
            super().__init__()
        def __next__(self):
            return next(self.gen)
        def __repr__(self):
            return f"{__class__.__name__}({repr(self.gen)})"

    @_classtools.Overclass
    class Derived:
        fixedoverclass = None
        def __init__(self, *sources, **kwargs):
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
            super().__init__(**kwargs)
            self.register_argskwargs(*sources) # pylint: disable=E1101
        def __getitem__(self, arg):
            return self._sourceget_(self, arg)

    class Transform(Derived):
        def __init__(self, operator, /, *operands, **kwargs):
            self.operands, self.operator = operands, operator
            isdim = tuple(isinstance(op, Dimension) for op in operands)
            nisdim = isdim.count(True)
            if all(isdim):
                self.iter_fn = _partial(map, operator, *operands)
            elif not nisdim:
                raise ValueError("No dims in input!")
            else:
                if nisdim == 1:
                    self.iterlen = operands[isdim.index(True)].iterlen
                getops = lambda: (
                    op if isinstance(op, Dimension) else _repeat(op)
                        for op in operands
                    )
                self.iter_fn = _partial(map, operator, *getops())
            super().__init__(operator, *operands, **kwargs)
    @classmethod
    def operate(cls, *args, **kwargs):
        return cls.Transform(*args, **kwargs)

    class Slice(Derived):
        def __init__(self, source, incisor, /, **kwargs):
            self.source, self.incisor = source, incisor
            super().__init__(source, **kwargs)
            self.register_argskwargs(incisor) # pylint: disable=E1101


###############################################################################
###############################################################################
