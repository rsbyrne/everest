###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod
from collections import abc as _collabc
from functools import (
    lru_cache as _lru_cache,
    cached_property as _cached_property,
    reduce as _reduce,
    partial as _partial,
    )
import itertools as _itertools
import operator as _operator
import weakref as _weakref
import warnings as _warnings

from . import _special, _seqmerge
from .datalike import *

from .exceptions import *

class FuncyUnpackable(FuncyGeneric):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyUnpackable:
            if all((
                    issubclass(C, FuncyIterable),
                    not issubclass(C, FuncyMapping),
                    not issubclass(C, (tuple, str, FuncyDatalike)),
                    )):
                return True
        return NotImplemented

class FuncyStruct(FuncyGeneric):
    @classmethod
    def __subclasshook__(cls, C):
        if cls is FuncyStruct:
            if all((
                    issubclass(C, FuncyCollection),
                    not issubclass(C, FuncyMutableSequence),
                    not issubclass(C, FuncyUnpackable),
                    not issubclass(C, FuncyMapping),
                    not issubclass(C, FuncyString),
                    )):
                return True
        return NotImplemented
    @_abstractmethod
    def __len__(self):
        raise FuncyAbstractMethodException
# _ = FuncyStruct.register(tuple)

class FuncyIncisor(FuncyGeneric):
    ...

class FuncyTrivialIncisor(FuncyIncisor):
    ...
_ = FuncyTrivialIncisor.register(type(Ellipsis))

class FuncyShallowIncisor(FuncyIncisor):
    ...

class FuncyStrictIncisor(FuncyShallowIncisor):
    ...
_ = FuncyStrictIncisor.register(FuncyIntegral)
_ = FuncyStrictIncisor.register(FuncyString)

class FuncyDeclarativeIncisor(FuncyStrictIncisor):
    ...
_ = FuncyDeclarativeIncisor.register(FuncyMapping)

class FuncyBroadIncisor(FuncyShallowIncisor):
    ...
_ = FuncyBroadIncisor.register(FuncyUnpackable)

class FuncySeqIncisor(FuncyBroadIncisor):
    ...

class FuncySoftIncisor(FuncyBroadIncisor):
    ...
_ = FuncyBroadIncisor.register(FuncySlice)

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
    nArgs = len(args)
    if nArgs == 0:
        return args
    elif nArgs == 1:
        if args[0] is Ellipsis:
            return tuple(filler() for _ in range(depth))
        else:
            return args
    elif nArgs < depth:
        nEllipses = len(tuple(el for el in args if el is Ellipsis))
        if nEllipses == 0:
            return args
        elif nEllipses == 1:
            out = []
            for arg in args:
                if arg is Ellipsis:
                    for _ in range(depth - nArgs):
                        out.append(filler())
                else:
                    out.append(arg)
            return tuple(out)
        else:
            raise IndexError(f"Too many ellipses ({nEllipses} > 1)")
    elif nArgs == depth:
        return args
    else:
        raise IndexError(f"Too many args ({nArgs} > {depth})")

class FuncyIncisable(FuncySequence):
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
            (FuncyEvaluable, cls._getitem_evaluable),
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
        if incisionMethod is NotImplemented: raise TypeError(arg, type(arg))
        return incisionMethod(self, arg)
    def _getitem_generator(self, arg):
        raise NotYetImplemented
    def _getitem_evaluable(self, arg, /):
        return self[arg.value]
    def _getitem_trivial(self,
            arg: FuncyTrivialIncisor = None, /
            ) -> FuncyDatalike:
        return self
    def _incision_finalise(self, arg):
        return arg
    @property
    def incisors(self):
        return
        yield
    def _index_sets(self) -> 'Generator[Generator]':
        return
        yield
    def _index_types(self) -> 'Generator[type]':
        return
        yield
    def _get_indi(self, arg, /):
        argType = type(arg)
        for i, typ in list(enumerate(self._index_types()))[::-1]:
            if issubclass(argType, typ):
                return i
        raise TypeError(
            f"Incisor type {type(self)}"
            f" cannot be incised by arg type {type(arg)}"
            )
    def _indices(self) -> 'Generator[tuple]':
        return zip(*self._index_sets())
    def indices(self):
        for _, o in zip(range(1_000), self._indices()):
            yield o
    def _prime_indices(self):
        try:
            yield from next(self._index_sets())
        except StopIteration:
            yield from ()
    def __len__(self):
        return 0
    def __iter__(self):
        for _, o in zip(range(1_000), self._prime_indices()):
            yield self._incision_finalise(o)
#     @property
#     def value(self) -> object:
#         return iter(self) 
#     @value.setter
#     def value(self, val, /) -> None:
#         raise AttributeError
#     @value.deleter
#     def value(self) -> None:
#         raise AttributeError

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
    def _getitem_deep(self, args) -> FuncyDatalike:
        nArgs = len(args)
        if nArgs == 0:
            return self
        else:
            args = process_ellipsis(args, len(self.shape), filler = IgnoreDim)
            if (nArgs := len(args)) < (nLevels := self.nLevels):
                args = tuple((
                    *args, *(ignoredim for _ in range(nLevels - nArgs))
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
    @_abstractmethod
    def shape(self):
        raise FuncyAbstractMethodException
    @property
    def depth(self):
        return len(self.shape)
    def __len__(self):
        return self.shape[self.nLevels - 1]
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
    def nLevels(self):
        return len(self.levels)
    @property
    def _levelTractable(self):
        return not isinstance(
            self.__len__(),
            (_special.Unknown, _special.Null)
            )

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
    @classmethod
    def _get_incision_method(cls, arg, /):
        if isinstance(arg, FuncyPotentiallySeqlike):
            if arg.isSeq:
                return cls._getitem_seq
        return super()._get_incision_method(arg)

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
        indi = self._get_indi(arg)
        for inds in self._indices():
            if arg == inds[indi]:
                return self._get_incision_type('strict')(self, inds[0])
        raise IndexError(arg)
    def _getitem_broad(self, arg: FuncyBroadIncisor, /):
        if type(arg) is slice:
            if arg == slice(None):
                return self
        return self._get_incision_type('broad')(self, arg)
    def _index_sets(self):
        yield from super()._index_sets()
        if self._levelTractable:
            yield range(self.__len__())
        else:
            yield _itertools.count()
    def _index_types(self):
        yield from super()._index_types()
        yield FuncyIntegral

class FuncyIncision(FuncyDeepIncisable):
    def __init__(self, source, /, *args, **kwargs):
        self._source = source
        super().__init__(*args, **kwargs)
    @property
    def source(self):
        return self._source
    @property
    def truesource(self):
        source = self.source
        if isinstance(source, FuncyIncision): return source.truesource
        else: return source
    @property
    def shape(self):
        return self.source.shape
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
    def _incision_finalise(self, args):
        return self.source._incision_finalise(args)

class FuncyDeepIncision(FuncyIncision):
    def __init__(self, source, levels, /, *args, **kwargs):
        self._inheritedLevels = {**levels}
        super().__init__(source, *args, **kwargs)
    @property
    def shape(self):
        return self.levels[self.nLevels - 1].shape
    def _levels(self):
        yield from self._inheritedLevels.values()
    def __getitem__(self, arg, /):
        if not type(arg) is tuple:
            arg = (arg,)
        return super().__getitem__(arg)
    def _index_sets(self):
        yield _seqmerge.muddle((
            level._prime_indices() for level in self._levels()
            ))
    def _index_types(self):
        yield object
    def __iter__(self):
        for _, o in zip(range(1_000), self._prime_indices()):
            yield self._incision_finalise(o)

class FuncySubIncision(FuncyIncision):
    def _levels(self):
        yield from super()._levels()
        yield self
    def _index_sets(self) -> 'Generator[Generator]':
        yield range(self.__len__())
        yield from super()._index_sets()
    def _index_types(self):
        yield object
        yield from super()._index_types()

class FuncyShallowIncision(FuncyIncision):
    def __init__(self, source, incisor, /, *args, **kwargs):
        self._incisor = incisor
        super().__init__(source, *args, **kwargs)
    @property
    def incisor(self):
        return self._incisor
    @property
    def incisors(self):
        yield from self.source.incisors
        yield self.incisor
    def __len__(self):
        return _special.unkint
    @property
    def shape(self):
        shape = super().shape
        return tuple((
            *shape[:self.nLevels - 1],
            self.__len__(),
            *shape[self.nLevels:],
            ))
    def _levels(self):
        *levels, _ = super()._levels()
        yield from levels
        yield self

class FuncyStrictIncision(FuncyShallowIncision):
    def __len__(self):
        return 1
    def _index_sets(self):
        yield (self.incisor,)
    def _index_types(self):
        yield objectaa
#     @property
#     def value(self) -> object:
#         return tuple(iter(self))[0]

class FuncySeqIncision(FuncyShallowIncision, FuncySoftIncisable):
    def __len__(self):
        try: return len(self.incisor)
        except AttributeError: return super().__len__()
    def _index_sets(self):
        yield self.incisor
        yield from super()._index_sets()
    def _index_types(self):
        yield object
        yield from super()._index_types()

class FuncyBroadIncision(FuncyShallowIncision, FuncySoftIncisable):
    def _indices_getslice(self):
        inc, src = self.incisor, self.source
        return _itertools.islice(
            src._indices(),
            inc.start, inc.stop, inc.step
            )
    def _indices_getinterval(self):
        inc, src = self.incisor, self.source
        start, stop, step = inc.start, inc.stop, inc.step
        start = 0 if start is None else start
        stop = _special.infint if stop is None else stop
        starti, stopi, stepi = (src._get_indi(s) for s in (start, stop, step))
        it = src._indices()
        started = False
        stopped = False
        try:
            while not started:
                inds = next(it)
                started = inds[starti] >= start
            if step is None:
                inner_loop = lambda _: next(it)
            else:
                def inner_loop(inds):
                    stepped = False
                    thresh = inds[stepi] + step
                    while not stepped:
                        inds = next(it)
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
        for i, inds in _seqmerge.muddle((inc, src._indices())):
            if i == inds[src._get_indi(i)]:
                yield inds
    def _indices_getmask(self):
        inc, src = self.incisor, self.source
        for mask, inds in zip(src._indices(), inc):
            if mask:
                yield inds
    def _indices(self) -> 'Generator[tuple]':
        try:
            iterFn = self._iterFn
        except AttributeError:
            incisor = self.incisor
            if isinstance(incisor, FuncySlice):
                ss = incisor.start, incisor.stop, incisor.step
                if all(
                        isinstance(s, (FuncyNoneType, FuncyIntegral))
                            for s in ss
                        ):
                    iterFn = self._indices_getslice
                else:
                    iterFn = self._indices_getinterval
            elif isinstance(incisor, FuncyIterable):
                if all(isinstance(i, FuncyBool) for i in incisor):
                    iterFn = self._indices_getmask
                else:
                    iterFn = self._indices_getkeys
            else:
                raise TypeError(incisor, type(incisor))
            self._iterFn = iterFn
        return (
            (*srcinds, *slfinds)
                for srcinds, slfinds in zip(
                    iterFn(),
                    zip(*super()._index_sets()),
                    )
            )
    def _index_sets(self):
        return zip(*self._indices())
    def _index_types(self):
        yield from self.source._index_types()
        yield from super()._index_types()

###############################################################################
''''''
###############################################################################
