###############################################################################
'''The module defining the top-level 'incisable' types.'''
###############################################################################

from collections import abc as _collabc
from functools import (
    partial as _partial,
    )
import itertools as _itertools

from . import _special, _abstract

from . import incisor as _incisor

# DefaultObj = type('DefaultObj', (object,), dict())
# defaultobj = DefaultObj()

def process_depth(
        args: tuple, depth: int, /,
        filler = _incisor.trivial,
        ):
    args = tuple(arg if arg != slice(None) else filler for arg in args)
    if (not depth < _special.infint) and (Ellipsis in args):
        raise ValueError("Cannot use ellipsis when depth is infinite.")
    nargs = len(args)
    if nargs == 0:
        return args
    if nargs == 1:
        if args[0] is Ellipsis:
            return tuple(filler for _ in range(depth))
        return args
    if nargs < depth:
        nellipses = len(tuple(el for el in args if el is Ellipsis))
        if nellipses == 0:
            return args
        if nellipses == 1:
            out = []
            for arg in args:
                if arg is Ellipsis:
                    for _ in range(depth - nargs):
                        out.append(filler)
                else:
                    out.append(arg)
            return tuple(out)
        raise IndexError(f"Too many ellipses ({nellipses} > 1)")
    if nargs == depth:
        return tuple(filler if arg is Ellipsis else arg for arg in args)
    raise IndexError(
        f"Not enough depth to accommodate requested levels:"
        f" levels = {nargs} > depth = {depth})"
        )

class FuncyIncisable:
    _length = NotImplemented
    _maxcount = 1_000_000
    _depth = _special.infint
    _sub = None
    def __init__(self, *args, lev = None, **kwargs):
        subkw = self._subkwargs = dict()
        if not lev is None:
            if isinstance(lev, tuple):
                depth = len(lev)
                lev, *levn = lev
                subkw['lev'] = tuple(levn)
            else:
                depth = 1
            self._length = lev
            self._depth = depth
        super().__init__(*args, **kwargs)
    @property
    def subkwargs(self):
        return self._subkwargs
    @property
    def incisiontypes(self):
        return dict(
            trivial = type(self),
            sub = _incisiontypes.FuncySubIncision,
            deep = _incisiontypes.FuncyDeepIncision,
            broad = _incisiontypes.FuncyBroadIncision,
            strict = _incisiontypes.FuncyStrictIncision,
            )
    def _get_incision_type(self, arg: str, /):
        return self.incisiontypes[arg]
    @classmethod
    def _incision_methods(cls):
        yield from (
            (_abstract.general.FuncyEvaluable, cls._getitem_evaluable),
            (_collabc.Generator, cls._getitem_generator),
            (_incisor.FuncyTrivialIncisor, cls._getitem_trivial),
            (_incisor.FuncySubIncisor, cls._getitem_sub),
            (_incisor.FuncyDeepIncisor, cls._getitem_deep),
            (_incisor.FuncyStrictIncisor, cls._getitem_strict),
            (_incisor.FuncyBroadIncisor, cls._getitem_broad),
            )
    @classmethod
    def get_incision_method(cls, arg, /):
        argtyp = type(arg)
        for typ, meth in cls._incision_methods():
            if issubclass(argtyp, typ):
                return meth
        return NotImplemented
    def __getitem__(self, arg: _incisor.FuncyIncisor, /):
        incmeth = self.get_incision_method(arg)
        if incmeth is NotImplemented:
            raise TypeError(arg, type(arg))
        return incmeth(self, arg)
    def _getitem_generator(self, arg):
        return self[list(arg)]
    def _getitem_evaluable(self, arg, /):
        return self[arg.value]
    def _getitem_trivial(self,
            _: _incisor.FuncyTrivialIncisor = None, /
            ) -> _abstract.datalike.FuncyDatalike:
        return self
    def _getitem_sub(self, _, /):
        return self._get_incision_type('sub')(self, **self.subkwargs)
    def _getitem_deep(self, args) -> _abstract.datalike.FuncyDatalike:
        if args is Ellipsis:
            args = (Ellipsis,)
        nargs = len(args)
        if nargs == 0:
            return self
        args = process_depth(args, self.depth)
        if (nargs := len(args)) < (nlevels := self.nlevels):
            args = tuple((
                *args, *(_incisor.trivial for _ in range(nlevels - nargs))
                ))
        argiter, levels = iter(args), self.levels()
        cursor = next(levels)[next(argiter)]
        for arg, lev in _itertools.zip_longest(argiter, levels):
            cursor = cursor[_incisor.subinc]
            if hasattr(lev, 'incisors'):
                for inc in lev.incisors:
                    cursor = cursor[inc]
            cursor = cursor[arg]
        return self._get_incision_type('deep')(cursor)
    def _getitem_broad(self, arg, /):
        return self._get_incision_type('broad')(arg, self)
    def _getitem_strict(self, arg, /):
        return self._get_incision_type('strict')(arg, self)
    def __call__(self, arg0, /, *argn):
        if not argn:
            return arg0
        return tuple((arg0, *argn))
    def _get_end_info(self):
        raise TypeError(f"Cannot index type {type(self)}")
    @property
    def length(self):
        if (length := self._length) is None:
            length, _ = self._get_end_info()
        return length
    def lengths(self):
        yield self.length
    @property
    def shape(self):
        return tuple(self.lengths)
    @property
    def depth(self):
        return self._depth
    def levels(self):
        yield self
    @property
    def levelsdict(self):
        return dict(enumerate(self.levels()))
    def _get_level(self, i):
        try:
            return self.levelsdict[i]
        except KeyError:
            return None
    @property
    def nlevels(self):
        return len(self.levelsdict)
    @property
    def tractable(self):
        return not isinstance(
            self.length,
            (_special.Unknown, _special.Infinite,
            _special.BadNumber, type(NotImplemented)),
            )
    def __len__(self):
        if self.tractable:
            return self.length
        raise ValueError("Cannot measure length of this object.")
    def indices(self):
        raise TypeError(f"Cannot index type {type(self)}")

def safe_iterate(iterator, maxcount):
    iterator = enumerate(iterator)
    count, iterant = None, None
    for count, iterant in iterator:
        if count > maxcount:
            raise RuntimeError("Max count exceeded on incision iter.")
        yield count, iterant

class FuncySoftIncisable(FuncyIncisable):

    _endind = None
    _endval = None
    _length = _special.infint

    @property
    def incisiontypes(self):
        return {**super().incisiontypes, **dict(
            soft = _incisiontypes.FuncySoftIncision,
            sub = _incisiontypes.FuncySoftSubIncision,
            )}
    @classmethod
    def _incision_methods(cls):
        yield (_incisor.FuncySoftIncisor, cls._getitem_soft)
        yield from super()._incision_methods()
    def _getitem_strict(self, arg, /):
        indi = self.get_indi(arg)
        for inds in self.allindices():
            if arg == inds[indi]:
                return self._get_incision_type('strict')(inds[0], self)
        raise IndexError(arg)
    def _getitem_soft(self, arg, /):
        if isinstance(arg, slice):
            if arg == slice(None):
                return self
        return self._get_incision_type('soft')(arg, self)

    def index_sets(self) -> 'Generator[Generator]':
        try:
            yield range(self._length)
        except (ValueError, TypeError):
            yield _itertools.count()
    def index_types(self) -> 'Generator[type]':
        yield _abstract.datalike.FuncyIntegral
    def get_indi(self, arg, /):
        argtyp = type(arg)
        for i, typ in list(enumerate(self.index_types()))[::-1]:
            if issubclass(argtyp, typ):
                return i
        raise TypeError(
            f"Incisor type {type(self)}"
            f" cannot be incised by arg type {type(arg)}"
            )
    def allindices(self) -> 'Generator[tuple]':
        return zip(*self.index_sets())
    def indices(self):
        return iter(next(self.index_sets()))
    def __iter__(self):
        return (
            self(ind)
                for _, ind in safe_iterate(
                    self.indices(),
                    self._maxcount,
                    )
            )
    def _get_end_info(self):
        length, endind = None, None
        try:
            iterator = safe_iterate(self.allindices(), self._maxcount)
            for length, endind in iterator:
                ...
            if length is None:
                length = 0
            else:
                length += 1
        except RuntimeError:
            length, endind = _special.unkint, _special.unkint
        self._length, self._endind = length, endind
        return length, endind
    @property
    def endind(self):
        if (endind := self._endind) is None:
            _, endind = self._get_end_info()
        return endind
    @property
    def endval(self):
        if (endval := self._endval) is None:
            endval = self._endval = self(self.endind[0])
        return endval

# at bottom to avoid circular import:
from . import incision as _incisiontypes

###############################################################################
###############################################################################
