###############################################################################
'''The module that defines the Incision Protocol.'''
###############################################################################

from abc import abstractmethod as _abstractmethod
from collections import abc as _collabc
from functools import (
    partial as _partial,
    )
import itertools as _itertools
import time as _time

from . import _special, _seqmerge
from .abstract import FuncyABC as _FuncyABC
from . import datalike as _datalike
from . import general as _general

from . import exceptions as _exceptions

# class IterLengthExceeded(_exceptions.FuncyAbstractException):
#     '''The iteration went on longer than the maximum allowed.'''

class FuncyUnpackable(_FuncyABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyUnpackable:
            if all((
                    issubclass(C, _datalike.FuncyIterable),
                    not issubclass(C, _datalike.FuncyMapping),
                    not issubclass(C, (tuple, str, _datalike.FuncyDatalike)),
                    )):
                return True
        return NotImplemented

class FuncyStruct(_FuncyABC):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyStruct:
            if all((
                    issubclass(C, _datalike.FuncyCollection),
                    not issubclass(C, _datalike.FuncyMutableSequence),
                    not issubclass(C, FuncyUnpackable),
                    not issubclass(C, _datalike.FuncyMapping),
                    not issubclass(C, _datalike.FuncyString),
                    )):
                return True
        return NotImplemented
    @_abstractmethod
    def __len__(self):
        raise _exceptions.FuncyAbstractMethodException
# _ = FuncyStruct.register(tuple)

class FuncyIncisor(_FuncyABC):
    ...

class FuncyTrivialIncisor(FuncyIncisor):
    ...
_ = FuncyTrivialIncisor.register(type(Ellipsis))

class FuncyShallowIncisor(FuncyIncisor):
    ...

class FuncyStrictIncisor(FuncyShallowIncisor):
    ...
_ = FuncyStrictIncisor.register(_datalike.FuncyIntegral)
_ = FuncyStrictIncisor.register(_datalike.FuncyString)

class FuncyDeclarativeIncisor(FuncyStrictIncisor):
    ...
_ = FuncyDeclarativeIncisor.register(_datalike.FuncyMapping)

class FuncyBroadIncisor(FuncyShallowIncisor):
    ...
_ = FuncyBroadIncisor.register(FuncyUnpackable)

class FuncySeqIncisor(FuncyBroadIncisor):
    ...

class FuncySoftIncisor(FuncyBroadIncisor):
    ...
_ = FuncyBroadIncisor.register(_general.FuncySlice)

class FuncyDeepIncisor(FuncyIncisor):
    ...
_ = FuncyDeepIncisor.register(FuncyStruct)

class FuncySubIncisor(FuncyDeepIncisor):
    ...
subinc = FuncySubIncisor()

# class FuncyRelegatedIncisor(FuncyIncisor):
#     def __init__(self, incisor):
#         self.incisor = incisor
#     def __call__(self):
#         return self.incisor

class IgnoreDim:
    ...
ignoredim = IgnoreDim()

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
        nEllipses = len(tuple(el for el in args if el is Ellipsis))
        if nEllipses == 0:
            return args
        if nEllipses == 1:
            out = []
            for arg in args:
                if arg is Ellipsis:
                    for _ in range(depth - nargs):
                        out.append(filler())
                else:
                    out.append(arg)
            return tuple(out)
        raise IndexError(f"Too many ellipses ({nEllipses} > 1)")
    if nargs == depth:
        return args
    raise IndexError(f"Too many args ({nargs} > {depth})")

def iter_indices(iterator, *, maxcount = 1_000_000):
    iterator = enumerate(iterator)
    count, out = None, None
    while True:
        try:
            count, out = next(iterator)
            if count > maxcount:
                raise RuntimeError("Max count exceeded on incision iter.")
            yield out
        except StopIteration:
            return count + 1, out

class FuncyIncisable(_datalike.FuncySequence):
    shape = ()
    def __init__(self,
            *args,
            shape,
            **kwargs,
            ):
        self.shape = shape
        super().__init__(*args, **kwargs)
    @property
    def incisionTypes(self):
        return dict(
            trivial = type(self),
            )
    def _get_incision_type(self, arg: str, /):
        return self.incisionTypes[arg]
    @classmethod
    def _incision_methods(cls):
        yield from (
            (_general.FuncyEvaluable, cls._getitem_evaluable),
            (_collabc.Generator, cls._getitem_generator),
            (FuncyTrivialIncisor, cls._getitem_trivial),
            )
    @classmethod
    def _get_incision_method(cls, arg, /):
        argType = type(arg)
        for typ, meth in cls._incision_methods():
            if issubclass(argType, typ):
                return meth
        return NotImplemented
    def __getitem__(self, arg: FuncyIncisor, /):
        incisionMethod = self._get_incision_method(arg)
        if incisionMethod is NotImplemented:
            raise TypeError(arg, type(arg))
        return incisionMethod(self, arg)
    def _getitem_generator(self, arg):
        raise _exceptions.NotYetImplemented
    def _getitem_evaluable(self, arg, /):
        return self[arg.value]
    def _getitem_trivial(self,
            arg: FuncyTrivialIncisor = None, /
            ) -> _datalike.FuncyDatalike:
        return self
    def incision_finalise(self, arg, /):
        return arg
    @property
    def incisors(self):
        return
        yield
    def index_sets(self) -> 'Generator[Generator]':
        return
        yield
    def index_types(self) -> 'Generator[type]':
        return
        yield
    def get_indi(self, arg, /):
        argType = type(arg)
        for i, typ in list(enumerate(self.index_types()))[::-1]:
            if issubclass(argType, typ):
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
        except StopIteration:
            yield from ()
    def __iter__(self):
        for ind in iter_indices(self.prime_indices()):
            yield self.incision_finalise(ind)
    def _exploratory_iter(self, *, maxcount = 1_000_000):
        iterator = iter_indices(self.indices(), maxcount = maxcount)
        try:
            while True:
                _ = next(iterator)
        except StopIteration as stope:
            return stope.value
    def _get_end_info(self):
        try:
            length, endind = self._exploratory_iter()
        except RuntimeError:
            length, endind = _special.unkint, _special.unkint
        self._levellength, self._endind = length, endind
        return length, endind
    @property
    def endind(self):
        if (endind := self._endind) is None:
            _, endind = self._get_end_info()
        return endind
    @property
    def depth(self):
        return len(self.shape)
    @property
    def levellength(self):
        length = (shp := list(self.shape))[(ind := (self.nlevels - 1))]
        if length is None:
            length, _ = self._get_end_info()
            shp[ind] = length
            self.shape = tuple(shp)
        return length
    @property
    def nlevels(self):
        return 1
    @property
    def tractable(self):
        return not isinstance(
            self.levellength,
            (_special.Unknown, _special.Infinite, _special.BadNumber)
            )
    def __len__(self):
        if self.tractable:
            return self.levellength
        raise ValueError("Cannot measure length of this object.")

class FuncyDeepIncisable(FuncyIncisable):
    @property
    def incisionTypes(self):
        return {**super().incisionTypes, **dict(
            sub = FuncySubIncision,
            deep = FuncyDeepIncision,
            )}
    @classmethod
    def _incision_methods(cls):
        yield from (
            (FuncySubIncisor, cls._getitem_sub),
            (FuncyDeepIncisor, cls._getitem_deep),
            )
        yield from super()._incision_methods()
    def _getitem_sub(self, _, /):
        return self._get_incision_type('sub')(self)
    def _getitem_deep(self, args) -> _datalike.FuncyDatalike:
        nargs = len(args)
        if nargs == 0:
            return self
        args = process_ellipsis(args, len(self.shape), filler = IgnoreDim)
        if (nargs := len(args)) < (nlevels := self.nlevels):
            args = tuple((
                *args, *(ignoredim for _ in range(nlevels - nargs))
                ))
        enum = enumerate(args)
        for i, arg in enum:
            if not isinstance(arg, IgnoreDim):
                break
            return self # because every dim was ignored
        cut = self._get_level(i)[arg]
        for i, arg in enum:
            cut = cut[subinc] # go next level down
            if not (precut := self._get_level(i)) is None:
                for inc in precut.incisors:
                    cut = cut[inc]
            if not isinstance(arg, IgnoreDim):
                cut = cut[arg]
        return self._get_incision_type('deep')(cut.truesource, cut.levels)
    @property
    def depth(self):
        return len(self.shape)
    def _levels(self):
        yield self
    @property
    def levels(self):
        return dict(enumerate(self._levels()))
    def _get_level(self, i):
        try:
            return self.levels[i]
        except KeyError:
            return None
    @property
    def nlevels(self):
        return len(self.levels)

class FuncyHardIncisable(FuncyDeepIncisable):
    @property
    def incisionTypes(self):
        return {**super().incisionTypes, **dict(
            seq = FuncySeqIncision,
            declarative = FuncyStrictIncision,
            )}
    @classmethod
    def _incision_methods(cls):
        yield from (
            (FuncyDeclarativeIncisor, cls._getitem_declarative),
            (FuncyUnpackable, cls._getitem_seq),
            )
        yield from super()._incision_methods()
    def _getitem_seq(self, arg, /):
        return self._get_incision_type('seq')(self, arg)
    def _getitem_declarative(self, arg):
        return self._get_incision_type('declarative')(self, arg)

class FuncySoftIncisable(FuncyDeepIncisable):
    @property
    def incisionTypes(self):
        return {**super().incisionTypes, **dict(
            broad = FuncyBroadIncision,
            strict = FuncyStrictIncision,
            )}
    @classmethod
    def _incision_methods(cls):
        yield (FuncyStrictIncisor, cls._getitem_strict)
        yield (FuncyBroadIncisor, cls._getitem_broad)
        yield from super()._incision_methods()
    def _getitem_strict(self, arg, /):
        indi = self.get_indi(arg)
        for inds in self.indices():
            if arg == inds[indi]:
                return self._get_incision_type('strict')(self, inds[0])
        raise IndexError(arg)
    def _getitem_broad(self, arg: FuncyBroadIncisor, /):
        if isinstance(arg, slice):
            if arg == slice(None):
                return self
        return self._get_incision_type('broad')(self, arg)
    def index_sets(self):
        yield from super().index_sets()
        try:
            yield range(self.shape[self.nlevels - 1])
        except (ValueError, TypeError):
            yield _itertools.count()
    def index_types(self):
        yield from super().index_types()
        yield _datalike.FuncyIntegral

class FuncyIncision(FuncyDeepIncisable):
    def __init__(self, source, /, *args, **kwargs):
        self._source = source
        super().__init__(*args, shape = source.shape, **kwargs)
    @property
    def source(self):
        return self._source
    @property
    def truesource(self):
        source = self.source
        if isinstance(source, FuncyIncision):
            return source.truesource
        return source
    def _levels(self):
        return self.source._levels()
    @property
    def incisionTypes(self):
        return {**self.source.incisionTypes, **super().incisionTypes}
    def _get_incision_method(self, arg, /):
        meth = super()._get_incision_method(arg)
        if meth is NotImplemented:
            meth = self.source._get_incision_method(arg)
        return meth
    def incision_finalise(self, arg, /):
        return self.source.incision_finalise(arg)

class FuncyDeepIncision(FuncyIncision):
    def __init__(self, source, levels, /, *args, **kwargs):
        self._inheritedlevels = {**levels}
        super().__init__(source, *args, **kwargs)
    @property
    def shape(self):
        return self.levels[self.nlevels - 1].shape
    def _levels(self):
        yield from self._inheritedlevels.values()
    def __getitem__(self, arg, /):
        if not isinstance(arg, tuple):
            arg = (arg,)
        return super().__getitem__(arg)
    def index_sets(self):
        yield _seqmerge.muddle((
            level.prime_indices() for level in self._levels()
            ))
    def index_types(self):
        yield object

class FuncySubIncision(FuncyIncision):
    def _levels(self):
        yield from super()._levels()
        yield self
    def index_sets(self) -> 'Generator[Generator]':
        yield range(len(self))
        yield from super().index_sets()
    def index_types(self):
        yield object
        yield from super().index_types()

class FuncyShallowIncision(FuncyIncision):
    _default_levellength = None
    def __init__(self,
            source, incisor, /, *args,
            _default_levellength = None, **kwargs
            ):
        self.incisor = incisor
        super().__init__(source, *args, **kwargs)
        shp = list(self.shape)
        deflength = _default_levellength
        if deflength is None:
            deflength = self._default_levellength
        shp[self.nlevels -1] = deflength
        self.shape = tuple(shp)
    @property
    def incisors(self):
        yield from self.source.incisors
        yield self.incisor
    def _levels(self):
        *levels, _ = super()._levels()
        yield from levels
        yield self

class FuncyStrictIncision(FuncyShallowIncision):
    _default_levellength = 1
    def index_sets(self):
        yield (self.incisor,)
    def index_types(self):
        yield object

class FuncySeqIncision(FuncyShallowIncision, FuncySoftIncisable):
    def __init__(self, source, incisor, *args, **kwargs):
        super().__init__(
            *args, source, incisor,
            _default_levellength = len(incisor), **kwargs,
            )
    def index_sets(self):
        yield self.incisor
        yield from super().index_sets()
    def index_types(self):
        yield object
        yield from super().index_types()

class FuncyBroadIncision(FuncyShallowIncision, FuncySoftIncisable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.iter_fn = self._get_iter_fn()
    def _indices_getslice(self):
        inc, src = self.incisor, self.source
        return _itertools.islice(
            src.indices(),
            inc.start, inc.stop, inc.step
            )
    def _indices_getinterval(self):
        inc, src = self.incisor, self.source
        start, stop, step = inc.start, inc.stop, inc.step
        start = 0 if start is None else start
        stop = _special.infint if stop is None else stop
        starti, stopi, stepi = (src.get_indi(s) for s in (start, stop, step))
        itr = src.indices()
        started = False
        stopped = False
        try:
            while not started:
                inds = next(itr)
                started = inds[starti] >= start
            if step is None:
                inner_loop = lambda _: next(itr)
            else:
                def inner_loop(inds):
                    stepped = False
                    thresh = inds[stepi] + step
                    while not stepped:
                        inds = next(itr)
                        stepped = inds[stepi] >= thresh
                    return inds
            while not stopped:
                yield inds
                inds = inner_loop(inds)
                stopped = inds[stopi] >= stop
        except StopIteration:
            pass
    def _indices_getkeys(self):
        inc, src = self.incisor, self.source
        for i, inds in _seqmerge.muddle((inc, src.indices())):
            if i == inds[src.get_indi(i)]:
                yield inds
    def _indices_getmask(self):
        inc, src = self.incisor, self.source
        for mask, inds in zip(src.indices(), inc):
            if mask:
                yield inds
    def _get_iter_fn(self):
        incisor = self.incisor
        if isinstance(incisor, _general.FuncySlice):
            _ss = incisor.start, incisor.stop, incisor.step
            if all(
                    isinstance(s, (
                            _general.FuncyNoneType,
                            _datalike.FuncyIntegral
                            ))
                        for s in _ss
                    ):
                return self._indices_getslice
            return self._indices_getinterval
        if isinstance(incisor, _datalike.FuncyIterable):
            if all(isinstance(i, _datalike.FuncyBool) for i in incisor):
                return self._indices_getmask
            return self._indices_getkeys
        raise TypeError(incisor, type(incisor))
    def indices(self) -> 'Generator[tuple]':
        return (
            (*srcinds, *slfinds)
                for srcinds, slfinds in zip(
                    self.iter_fn(),
                    zip(*super().index_sets()),
                    )
            )
    def index_sets(self):
        return zip(*self.indices())
    def index_types(self):
        yield from self.source.index_types()
        yield from super().index_types()

###############################################################################
###############################################################################
