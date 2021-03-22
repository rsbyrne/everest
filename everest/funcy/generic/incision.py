################################################################################

from abc import ABC as _ABC, abstractmethod as _abstractmethod
from collections import abc as _collabc
from functools import (
    lru_cache as _lru_cache,
    reduce as _reduce,
    partial as _partial,
    )
import itertools as _itertools
import operator as _operator
import weakref as _weakref

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

# class FuncyRelegatedIncisor(FuncyIncisor):
#     def __init__(self, incisor):
#         self.incisor = incisor
#     def __call__(self):
#         return self.incisor

class FuncyIncisable(FuncySequence):
    @property
    def incisionTypes(self):
        return dict(
            trivial = type(self),
            sub = FuncySubIncision,
            single = FuncySingleIncision,
            )
    def _get_incision_type(self, arg: str, /):
        return self.incisionTypes[arg]
    @classmethod
    def _incision_methods(cls):
        yield from (
            (FuncyEvaluable, cls._getitem_evaluable),
            (_collabc.Generator, cls._getitem_generator),
            (FuncyTrivialIncisor, cls._getitem_trivial),
            (FuncyDeepIncisor, cls._getitem_deep),
            )
    @classmethod
    def _get_incision_method(cls, arg, /):
        argType = type(arg)
        for typ, meth in cls._incision_methods():
            if issubclass(argType, typ):
                return meth
        return NotImplemented
    def _getitem_generator(self, arg):
        raise NotYetImplemented
    def _getitem_evaluable(self, arg, /):
        return self[arg.value]
    def _getitem_trivial(self,
            arg: FuncyTrivialIncisor = None, /
            ) -> FuncyDatalike:
        return self
    def _getitem_deep(self, args) -> FuncyDatalike:
        nArgs = len(args)
        if nArgs == 0:
            return self._get_incision_type('sub')(self)
        elif nArgs == 1:
            return self[args[0]]
        else:
            arg0, *argn = process_ellipsis(args, self.depth)
            cut = self[arg0]
            if not isinstance(cut, self._get_incision_type('single')):
                cut = cut[()]
            argn = argn[0] if len(argn) == 1 else tuple(argn)
            return cut[argn]
    def __getitem__(self, arg: FuncyIncisor, /):
        incisionMethod = self._get_incision_method(arg)
        if incisionMethod is NotImplemented:
            raise TypeError(
                f"FuncyIncisor type {typ} not accepted."
                )
        return incisionMethod(self, arg)
    @_abstractmethod
    def _iter(self) -> 'Generator':
        raise FuncyAbstractMethodException
    @_abstractmethod
    def _incision_finalise(self, *args):
        raise FuncyAbstractMethodException
    @property
    @_abstractmethod
    def shape(self):
        raise FuncyAbstractMethodException
    def _iters(self) -> 'Generator[Generator]':
        yield self._iter()
    def _alliter(self):
        return _seqmerge.muddle(self._iters())
    def _metrics(self) -> 'Generator[tuple]':
        yield self._iter()
    def _items(self):
        return zip(zip(*self._metrics()), self._iter())
    def _metric_types(self):
        yield type(None) # nothing is a subclass of None
    def _get_meti(self, arg, /):
        argType = type(arg)
        for i, typ in enumerate(self._metric_types()):
            if issubclass(argType, typ):
                return i
        return 0
    def __len__(self):
        return self.shape[0]
    @property
    def depth(self):
        return len(self.shape)
    @property
    def level(self):
        return 0
    @property
    def _levelLength(self):
        return self.shape[self.level]
    @property
    def _supershape(self):
        return self.shape[:self.level]
    @property
    def _subshape(self):
        return self.shape[self.level + 1:]
    def __iter__(self):
        return (self._incision_finalise(*o) for o in self._alliter())

class FuncyHardIncisable(FuncyIncisable):
    @property
    def incisionTypes(self):
        return {**super().incisionTypes, 'seq': FuncySeqIncision}
    def _getitem_seq(self, arg, /):
        return self._get_incision_type('seq')(self, arg)
    @classmethod
    def _incision_methods(cls):
        yield from super()._incision_methods()
        yield from (
            (FuncyDeclarativeIncisor, cls._getitem_declarative),
            (FuncyUnpackable, cls._getitem_seq),
            )
    @classmethod
    def _get_incision_method(cls, arg, /):
        if isinstance(arg, FuncyPotentiallySeqlike):
            if arg.isSeq:
                return cls._getitem_seq
        return super()._get_incision_method(arg)
    def _getitem_declarative(self, arg, /):
        return self._incision_finalise(arg)
    def _iter(self) -> 'Generator':
        raise TypeError("Cannot iterate through HardIncisable.")
    def __iter__(self):
        raise TypeError("Cannot iterate through HardIncisable.")

class FuncySoftIncisable(FuncyIncisable):
    @property
    def incisionTypes(self):
        return {**super().incisionTypes, 'broad': FuncyBroadIncision}
    def _getitem_strict(self, arg, /):
        meti = self._get_meti(arg)
        for mets, v in self._items():
            if arg == mets[meti]:
                return self._get_incision_type('single')(self, v)
        raise IndexError
    def _getitem_broad(self, arg: FuncyBroadIncisor, /):
        if type(arg) is slice:
            if arg == slice(None):
                return self
        return self._get_incision_type('broad')(self, arg)
    @classmethod
    def _incision_methods(cls):
        yield from super()._incision_methods()
        yield from (
            (FuncyBroadIncisor, cls._getitem_broad),
            (FuncyStrictIncisor, cls._getitem_strict),
            )
    def _iter(self) -> 'Generator':
        return range(self._levelLength)
    def _metrics(self) -> 'Generator[tuple]':
        yield from super()._metrics()
        yield _itertools.count()
    def _metric_types(self):
        yield from super()._metric_types()
        yield FuncyIntegral

def process_ellipsis(args: tuple, depth: int, /):
    nArgs = len(args)
    if nArgs == 0:
        return args
    elif nArgs == 1:
        if args[0] is Ellipsis:
            return tuple(slice(None) for _ in range(depth))
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
                        out.append(slice(None))
                else:
                    out.append(arg)
            return tuple(out)
        else:
            raise IndexError(f"Too many ellipses ({nEllipses} > 1)")
    elif nArgs == depth:
        return args
    else:
        raise IndexError(f"Too many args ({nArgs} > {depth})")

class FuncyIncisionlike(FuncyIncisable):
    def __init__(self, source, /, *args, **kwargs):
        self._source = source
        super().__init__(*args, **kwargs)
    @property
    def source(self):
        return self._source
    @property
    def shape(self):
        return self.source.shape
    @property
    @_abstractmethod
    def level(self):
        raise FuncyAbstractMethodException
    @_abstractmethod
    def _iters(self) -> 'Generator[Generator]':
        raise FuncyAbstractMethodException
    def _get_incision_type(self, arg: str, /):
        return self.source._get_incision_type(arg)
    def _get_incision_method(self, arg, /):
        meth = super()._get_incision_method(arg)
        if meth is NotImplemented:
            meth = self.source._get_incision_method(arg)
        return meth
    def _get_meti(self, arg):
        return self.source._get_meti(arg)
    def _metrics(self):
        return self.source._metrics()
    def _incision_finalise(self, *args):
        return self.source._incision_finalise(*args)

class FuncyIncision(FuncyIncisionlike):
    def __init__(self, source, incisor, /, *args, **kwargs):
        self._incisor = incisor
        super().__init__(source, *args, **kwargs)
    @property
    def incisor(self):
        return self._incisor

class FuncyShallowIncision(FuncyIncision):
    @property
    def shape(self):
        source = self.source
        return tuple((
            *source._supershape,
            self._levelLength,
            *source._subshape,
            ))
    @property
    def level(self):
        return self.source.level
    @property
    def _levelLength(self):
        return _special.unkint
    def _iters(self) -> 'Generator[Generator]':
        *iters, _ = self.source._iters()
        yield from iters
        yield self._iter()

class FuncySeqIncision(FuncyShallowIncision, FuncySoftIncisable):
    @property
    def level(self):
        level = super().level
        assert level == 0
        return level
    def _iter(self) -> 'Generator':
        return ((inc,) for inc in self.incisor)

class FuncyBroadIncision(FuncyShallowIncision, FuncySoftIncisable):
    def _iter_getslice(self):
        inc = self.incisor
        return _itertools.islice(
            self.source._iter(),
            inc.start, inc.stop, inc.step
            )
    def _iter_getinterval(self):
        inc = self.incisor
        start, stop, step = inc.start, inc.stop, inc.step
        start = 0 if start is None else start
        stop = _special.infint if stop is None else stop
        startmeti, stopmeti, stepmeti = (
            self._get_meti(s) for s in (start, stop, step)
            )
        it = iter(self.source._items())
        started = False
        stopped = False
        try:
            while not started:
                mets, v = next(it)
                started = mets[startmeti] >= start
            if step is None:
                inner_loop = lambda _: next(it)
            else:
                def inner_loop(mets):
                    stepped = False
                    thresh = mets[stepmeti] + step
                    while not stepped:
                        mets, v = next(it)
                        stepped = mets[stepmeti] >= thresh
                    return mets, v
            while not stopped:
                yield v
                mets, v = inner_loop(mets)
                stopped = mets[stopmeti] >= stop
        except StopIteration:
            pass
    def _iter_getkeys(self):
        for i, (mets, v) in _seqmerge.muddle(
                (self.incisor, self.source._items())
                ):
            met = mets[self._get_meti(i)]
            if i == met:
                yield v
    def _iter_getmask(self):
        return (v for v, mask in zip(self.source._iter(), self.incisor) if mask)
    def _iter(self) -> 'Generator':
        try:
            return self._iterFn()
        except AttributeError:
            incisor = self.incisor
            if isinstance(incisor, FuncySlice):
                ss = incisor.start, incisor.stop, incisor.step
                if all(
                        isinstance(s, (FuncyNoneType, FuncyIntegral))
                            for s in ss
                        ):
                    iterFn = self._iter_getslice
                else:
                    iterFn = self._iter_getinterval
            elif isinstance(incisor, FuncyIterable):
                if all(isinstance(i, FuncyBool) for i in incisor):
                    iterFn = self._iter_getmask
                else:
                    iterFn = self._iter_getkeys
            else:
                raise TypeError(incisor, type(incisor))
            self._iterFn = iterFn
            return iterFn()

class FuncySingleIncision(FuncyShallowIncision):
    @property
    def _levelLength(self):
        return 1
    def _iter(self):
        return self.incisor
    def __getitem__(self, arg):
        return super().__getitem__(()).__getitem__(arg)

class FuncySubIncision(FuncyIncisionlike):
    @property
    def level(self):
        return self.source.level + 1
    def _iters(self) -> 'Generator[Generator]':
        yield from self.source._iters()
        yield self._iter()
    def _iter(self) -> 'Generator':
        return range(self._levelLength)

# class FuncySingleIncision(FuncyIncision):
#     @property
#     def shape(self):
#         source = self.source
#         return tuple((
#             *source._supershape,
#             1,
#             *source._subshape,
#             ))
#     @property
#     def level(self):
#         source = self.source
#         if isinstance(source, FuncySubIncision):
#             return source.level
#         else:
#             return source.level + 1
# #         return self.source.level + 1
#     def _iters(self) -> 'Generator[Generator]':
#         *iters, _ = self.source._iters()
#         yield from iters
#         yield self.incisor
#     def _iter(self) -> 'Generator':
#         raise TypeError(f"Cannot iterate through {type(self)}.")

# class FuncySubIncision(FuncyIncisionlike):
#     @property
#     def level(self):
#         return self.source.level + 1
#     def _iters(self) -> 'Generator[Generator]':
#         yield from self.source._iters()
#         yield self._iter()
#     def _iter(self) -> 'Generator':
#         return range(self._levelLength)
    
#     def _superiter(self):
#         return self.source._iter()
# #     def _subiter(self):
        
#     def _iter(self):
#         for superkeys, subkeys _seqmerge.muddle(
#             (self.source._iter(), range(self._levelLength()))
#             )

################################################################################
