###############################################################################
'''The module that defines the Incision Protocol.'''
###############################################################################

import itertools as _itertools

from . import _special, _seqmerge, _abstract

from .incisable import (
    FuncyIncisable as _FuncyIncisable,
    FuncySoftIncisable as _FuncySoftIncisable,
    )

class FuncyIncision(_FuncyIncisable):
    def __init__(self, source, /, *args, **kwargs):
        self._source = source
        super().__init__(*args, **kwargs)
    @property
    def source(self):
        return self._source
    @property
    def truesource(self):
        source = self.source
        if isinstance(source, FuncyIncision):
            return source.truesource
        return source
    @property
    def levelsource(self):
        if isinstance(src := self.source, FuncySubIncision):
            return src
        else:
            return self.truesource
    def levels(self):
        return self.source.levels()
    @property
    def incisiontypes(self):
        return {**self.source.incisiontypes, **super().incisiontypes}
    def _get_incision_method(self, arg, /):
        meth = super()._get_incision_method(arg)
        if meth is NotImplemented:
            meth = self.source._get_incision_method(arg)
        return meth
    def __call__(self, *args, **kwargs):
        return self.truesource(*args, **kwargs)

class FuncyDeepIncision(FuncyIncision):
    def __init__(self, levels, /, *args, **kwargs):
        self._inheritedlevels = {**levels}
        super().__init__(*args, **kwargs)
    def lengths(self):
        yield from self.levelsdict[self.nlevels - 1].lengths()
    def levels(self):
        yield from self._inheritedlevels.values()
    def __getitem__(self, arg, /):
        if not isinstance(arg, tuple):
            arg = (arg,)
        return super().__getitem__(arg)
    def index_sets(self):
        yield _seqmerge.muddle((
            level.prime_indices() for level in self.levels()
            ))
    def index_types(self):
        yield object
    def __call__(self, args, **kwargs):
        return super().__call__(*args, **kwargs)

class FuncySubIncision(FuncyIncision):
    @property
    def parentlevel(self):
        return self.levelsdict[self.nlevels - 2]
    @property
    def levelsource(self):
        return self.parentlevel.levelsource
    def lengths(self):
        yield from self.source.lengths()
        yield self.length
    def levels(self):
        yield from super().levels()
        yield self
    def index_sets(self) -> 'Generator[Generator]':
        yield from self.levelsource.index_sets()
    def index_types(self) -> 'Generator[type]':
        yield from self.levelsource.index_types()

class FuncyShallowIncision(FuncyIncision):
    def __init__(self, incisor, /, *args, **kwargs):
        self.incisor = incisor
        super().__init__(*args, **kwargs)
    @property
    def incisors(self):
        yield from self.source.incisors
        yield self.incisor
    def levels(self):
        *levels, _ = super().levels()
        yield from levels
        yield self

class FuncyStrictIncision(FuncyShallowIncision):
    _length = 1
    def index_sets(self):
        yield (self.incisor,)
    def index_types(self):
        yield object

class FuncySequenceIncision(FuncyShallowIncision, _FuncySoftIncisable):
    def __init__(self, incisor, /, *args, **kwargs):
        super().__init__(incisor, *args, length = len(incisor), **kwargs)
    def index_sets(self):
        yield self.incisor
        yield from super().index_sets()
    def index_types(self):
        yield object
        yield from super().index_types()

class FuncyBroadIncision(FuncyShallowIncision, _FuncySoftIncisable):
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
        for mask, inds in zip(inc, src.indices()):
            if mask:
                yield inds
    def _get_iter_fn(self):
        incisor = self.incisor
        if isinstance(incisor, _abstract.general.FuncySlice):
            _ss = incisor.start, incisor.stop, incisor.step
            if all(
                    isinstance(s, (
                            _abstract.general.FuncyNoneType,
                            _abstract.datalike.FuncyIntegral
                            ))
                        for s in _ss
                    ):
                return self._indices_getslice
            return self._indices_getinterval
        if isinstance(incisor, _abstract.datalike.FuncyIterable):
            if all(isinstance(i, _abstract.datalike.FuncyBool) for i in incisor):
                return self._indices_getmask
            return self._indices_getkeys
        raise TypeError(incisor, type(incisor))
    def index_sets(self):
        return zip(*(
            (*srcinds, *slfinds)
                for srcinds, slfinds in zip(
                    self.iter_fn(),
                    zip(*super().index_sets()),
                    )
            ))
    def index_types(self):
        yield from self.source.index_types()
        yield from super().index_types()

###############################################################################
###############################################################################
