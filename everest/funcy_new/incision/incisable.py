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

IgnoreDim = type('IgnoreDim', (object,), dict())
ignoredim = IgnoreDim()

DefaultObj = type('DefaultObj', (object,), dict())
defaultobj = DefaultObj()

def process_ellipsis(
        args: tuple, depth: int, /,
        filler = _partial(slice, None)
        ):
    nargs = len(args)
    if nargs == 0:
        return args
    if nargs == 1:
        if args[0] is Ellipsis:
            return tuple(filler() for _ in range(depth))
        return args
    if nargs < depth:
        nellipses = len(tuple(el for el in args if el is Ellipsis))
        if nellipses == 0:
            return args
        if nellipses == 1:
            if not depth < _special.infint:
                raise ValueError("Cannot use ellipsis when depth is infinite.")
            out = []
            for arg in args:
                if arg is Ellipsis:
                    for _ in range(depth - nargs):
                        out.append(filler())
                else:
                    out.append(arg)
            return tuple(out)
        raise IndexError(f"Too many ellipses ({nellipses} > 1)")
    if nargs == depth:
        return args
    raise IndexError(f"Too many args ({nargs} > {depth})")

def safe_iterate(iterator, maxcount):
    iterator = enumerate(iterator)
    count, iterant = None, None
    for count, iterant in iterator:
        if count > maxcount:
            raise RuntimeError("Max count exceeded on incision iter.")
        yield count, iterant

class FuncyIncisable:
    _endind = defaultobj
    _endval = defaultobj
    _length = defaultobj
    _maxcount = 1_000_000
    _index_sets = ()
    _index_types = ()
    _incisors = ()
    def __init__(self, *args, length = None, **kwargs):
        if not length is None:
            self._length = length
        super().__init__(*args, **kwargs)
    @property
    def incisiontypes(self):
        return dict(
            trivial = type(self),
            sub = _incisiontypes.FuncySubIncision,
            deep = _incisiontypes.FuncyDeepIncision,
            seq = _incisiontypes.FuncySequenceIncision,
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
            (_abstract.structures.FuncyUnpackable, cls._getitem_seq),
            )
    @classmethod
    def _get_incision_method(cls, arg, /):
        argType = type(arg)
        for typ, meth in cls._incision_methods():
            if issubclass(argType, typ):
                return meth
        return NotImplemented
    def __getitem__(self, arg: _incisor.FuncyIncisor, /):
        incisionMethod = self._get_incision_method(arg)
        if incisionMethod is NotImplemented:
            raise TypeError(arg, type(arg))
        return incisionMethod(self, arg)
    def _getitem_generator(self, arg):
        return self[list(arg)]
    def _getitem_evaluable(self, arg, /):
        return self[arg.value]
    def _getitem_trivial(self,
            _: _incisor.FuncyTrivialIncisor = None, /
            ) -> _abstract.datalike.FuncyDatalike:
        return self
    def _getitem_sub(self, _, /):
        return self._get_incision_type('sub')(self)
    def _getitem_deep(self, args) -> _abstract.datalike.FuncyDatalike:
        nargs = len(args)
        if nargs == 0:
            return self
        args = process_ellipsis(args, self.depth, filler = IgnoreDim)
        if (nargs := len(args)) < (nlevels := self.nlevels):
            args = tuple((
                *args, *(ignoredim for _ in range(nlevels - nargs))
                ))
        enum = enumerate(args)
        i, arg = defaultobj, defaultobj
        for i, arg in enum:
            if not isinstance(arg, IgnoreDim):
                break
            return self # because every dim was ignored
        assert not i is defaultobj
        cut = self._get_level(i)[arg]
        for i, arg in enum:
            cut = cut[_incisor.subinc] # go next level down
            if not (precut := self._get_level(i)) is None:
                for inc in precut.incisors:
                    cut = cut[inc]
            if not isinstance(arg, IgnoreDim):
                cut = cut[arg]
        return self._get_incision_type('deep')(cut.levelsdict, cut.truesource)
    def _getitem_seq(self, arg, /):
        return self._get_incision_type('seq')(arg, self)
    def _getitem_strict(self, arg, /):
        return self._get_incision_type('strict')(arg, self)
    def __call__(self, arg0, /, *argn):
        if not argn:
            return arg0
        return tuple((arg0, *argn))
    @property
    def incisors(self):
        yield from self._incisors
    def index_sets(self) -> 'Generator[Generator]':
        yield from self._index_sets
    def index_types(self) -> 'Generator[type]':
        yield from self._index_types
    def get_indi(self, arg, /):
        argtyp = type(arg)
        for i, typ in list(enumerate(self.index_types()))[::-1]:
            if issubclass(argtyp, typ):
                return i
        raise TypeError(
            f"Incisor type {type(self)}"
            f" cannot be incised by arg type {type(arg)}"
            )
    def indices(self) -> 'Generator[tuple]':
        return zip(*self.index_sets())
    def prime_indices(self):
        try:
            yield from next(self.index_sets())
        except StopIteration as exc:
            raise TypeError("This incisable has no indices.") from exc
    def __iter__(self):
        return (
            self(ind)
                for _, ind in safe_iterate(
                    self.prime_indices(),
                    self._maxcount,
                    )
            )
    def _get_end_info(self):
        try:
            for length, endind in safe_iterate(self.indices(), self._maxcount):
                ...
        except RuntimeError:
            length, endind = _special.unkint, _special.unkint
        if not isinstance(length, _special.BadNumber):
            length += 1
        self._length, self._endind = length, endind
        return length, endind
    @property
    def endind(self):
        if (endind := self._endind) is defaultobj:
            _, endind = self._get_end_info()
        return endind
    @property
    def endval(self):
        if (endval := self._endval) is defaultobj:
            endval = self._endval = self(self.endind[0])
        return endval
    @property
    def length(self):
        if (length := self._length) is defaultobj:
            length, _ = self._get_end_info()
        return length
    def lengths(self):
        yield self.length
    @property
    def shape(self):
        return tuple(self.lengths)
    @property
    def depth(self):
        return _special.infint
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
            (_special.Unknown, _special.Infinite, _special.BadNumber)
            )
    def __len__(self):
        if self.tractable:
            return self.length
        raise ValueError("Cannot measure length of this object.")

class FuncySoftIncisable(FuncyIncisable):
    @property
    def incisiontypes(self):
        return {**super().incisiontypes, **dict(
            broad = _incisiontypes.FuncyBroadIncision,
            )}
    @classmethod
    def _incision_methods(cls):
        yield (_incisor.FuncyStrictIncisor, cls._getitem_strict)
        yield (_incisor.FuncyBroadIncisor, cls._getitem_broad)
        yield from super()._incision_methods()
    def _getitem_strict(self, arg, /):
        indi = self.get_indi(arg)
        for inds in self.indices():
            if arg == inds[indi]:
                return self._get_incision_type('strict')(inds[0], self)
        raise IndexError(arg)
    def _getitem_broad(self, arg: _incisor.FuncyBroadIncisor, /):
        if isinstance(arg, slice):
            if arg == slice(None):
                return self
        return self._get_incision_type('broad')(arg, self)
    def index_sets(self):
        yield from super().index_sets()
        try:
            yield range(self._length)
        except (ValueError, TypeError):
            yield _itertools.count()
    def index_types(self):
        yield from super().index_types()
        yield _abstract.datalike.FuncyIntegral

# at bottom to avoid circular import:
from . import incision as _incisiontypes

###############################################################################
###############################################################################
