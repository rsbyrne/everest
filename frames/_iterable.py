from functools import wraps
import numbers
import warnings
from collections import OrderedDict
from collections.abc import Iterable as abcIterable
from collections.abc import Iterator as abcIterator

from funcy import Fn, convert, NullValueDetected
from wordhash import w_hash

from . import Frame
from ._stateful import Stateful, State
from ._indexable import Indexable, NotIndexlike, IndexableLoadFail
from ._producer import LoadFail, _producer_update_outs
from ._prompter import Prompter, _prompter_prompt_all

from ..exceptions import *
class IterableException(EverestException):
    pass
class IterableMissingAsset(MissingAsset, IterableException):
    pass
class IterableAlreadyInitialised(IterableException):
    pass
class IterableNotInitialised(IterableException):
    pass
class RedundantIterate(IterableException):
    pass
class IterableEnded(StopIteration, IterableException):
    pass
class BadStrategy(IterableException):
    pass
class ExhaustedStrategies(IterableException):
    pass

def _iterable_initialise_if_necessary(post = False):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if post:
                cond = self.initialised or self.postinitialised
            else:
                cond = self.initialised
            if not cond:
                self.initialise()
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
def _iterable_changed_state(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        pc = (i.data for i in self.indices)
        out = func(self, *args, **kwargs)
        nc = (i.data for i in self.indices)
        if nc != pc:
            self._iterable_changed_state_hook()
        return out
    return wrapper

class Iterable(Prompter, Indexable, Stateful):

    def __init__(self,
            **kwargs
            ):

        self.baselines = dict()

        super().__init__(**kwargs)

    def initialise(self, silent = False):
        if self.initialised:
            if silent:
                pass
            else:
                raise IterableAlreadyInitialised
        else:
            self._initialise()
            assert self.initialised
    def _initialise(self):
        self.indices.zero()
        self._iterable_changed_state_hook()
    @property
    def initialised(self):
        return self.indices.iszero
    @property
    def postinitialised(self):
        return self.indices.ispos
    def reset(self, silent = True):
        self.initialise(silent = silent)
    @_producer_update_outs
    @_prompter_prompt_all
    def _iterable_changed_state_hook(self):
        pass

    @property
    def stop(self):
        return self._stop()
    def _stop(self):
        return False
    def _check_stop(self, silent = False):
        if self.stop:
            if silent:
                return True
            raise IterableEnded
        return False

    @_iterable_initialise_if_necessary(post = True)
    def iterate(self, silent = False):
        if not self._check_stop(silent):
            self._iterate()
    def _iterate(self):
        self.indices['count'] += 1
        self._iterable_changed_state_hook()

    def _try_load(self, stop, silent = False):
        try: self.load(stop)
        except LoadFail: raise BadStrategy
    def _try_convert(self, stop):
        try: return convert(stop)
        except (ValueError, TypeError): raise BadStrategy
    def _try_index(self, stop):
        try: return self.indices.get_index(stop)
        except NotIndexlike: raise BadStrategy
    def _try_strats(self, *strats, **kwargs):
        for strat in strats:
            try: return strat(**kwargs)
            except BadStrategy: pass
        raise ExhaustedStrategies("Could not find a strategy to proceed.")
    def _get_stop_fn(self, stop):
        try:
            index = self._try_index(stop)
            return index >= stop
        except BadStrategy: pass
        try:
            stop = self._try_convert(stop)
            stop = stop.allclose(self)
        except BadStrategy: pass
        raise ExhaustedStrategies

    def reach(self, *args, **kwargs):
        if args:
            arg, *args = args
            self._reach(arg, **kwargs)
            if args:
                self.stride(*args, **kwargs)
        else:
            self._reach(**kwargs)
    def _reach(self, stop = IterableEnded, **kwargs):
        if stop is None:
            raise ValueError
        strats = (
            self._reach_end,
            self._try_load,
            self._reach_index,
            self._reach_fn
            )
        self._try_strats(*strats, stop = stop, **kwargs)
    def _reach_end(self, stop = IterableEnded, silent = True, **kwargs):
        if not type(stop) is type:
            raise BadStrategy
        if not issubclass(stop, StopIteration):
            raise BadStrategy
        stored = self.indices.stored[self.indices[0].name]
        if stored:
            i = max(stored)
            if i != self.indices[0]:
                self.load(i)
        self.go(silent = silent, **kwargs)
    @_iterable_initialise_if_necessary(post = True)
    def _reach_index(self, stop, index = None, silent = False):
        if index is None:
            index = self._try_index(stop)
        if index == stop:
            if silent: return
            else: raise RedundantIterate
        stored = self.indices.stored[index.name]
        try: latest = sorted(i for i in stored if i < index)[-1]
        except IndexError: latest = None
        if not latest is None:
            return self.load(latest)
        else:
            if index > stop:
                self.reset()
        stop = index >= stop
        while not stop:
            self.iterate(silent = silent)
    @_iterable_initialise_if_necessary(post = True)
    def _reach_fn(self, stop, **kwargs):
        stop = self._try_convert(stop)
        try:
            self.load(stop)
        except LoadFail:
            self.reset()
            closed = stop.allclose(self)
            while not closed:
                self.iterate(**kwargs)

    def stride(self, *args, **kwargs):
        if args:
            for arg in args:
                self._stride(arg, **kwargs)
        else:
            self._stride(**kwargs)
    def _stride(self, stop = IterableEnded, **kwargs):
        if stop is None:
            raise ValueError
        strats = (self._reach_end, self._stride_index, self._stride_fn)
        self._try_strats(*strats, stop = stop, **kwargs)
    @_iterable_initialise_if_necessary(post = True)
    def _stride_index(self, stop, **kwargs):
        index = self._try_index(stop)
        stop = (index + stop).value
        self._reach_index(stop, index = index, **kwargs)
    @_iterable_initialise_if_necessary(post = True)
    def _stride_fn(self, stop, **kwargs):
        stop = self._try_convert(stop)
        ind, val = self.indices.get_now()
        stop = (ind >= val) & stop
        try:
            self._try_load(stop)
        except BadStrategy:
            closed = stop.allclose(self)
            while not closed:
                self.iterate(**kwargs)

    @_iterable_initialise_if_necessary(post = True)
    def go(self, *args, **kwargs):
        if args:
            *args, arg = args
            if args:
                self.stride(*args, **kwargs)
            self._go(arg)
        else:
            self._go(**kwargs)
    def _go(self, stop = None, **kwargs):
        if stop is None:
            self._go_indefinite(**kwargs)
        elif issubclass(type(stop), numbers.Integral):
            self._go_integral(stop, **kwargs)
        else:
            strats = (self._go_index, self._go_fn)
            self._try_strats(*strats, stop = stop, **kwargs)
    def _go_indefinite(self, silent = True):
        if not silent:
            warnings.warn("Running indefinitely - did you intend this?")
        while True:
            try:
                self.iterate()
            except IterableEnded:
                if silent:
                    return
                else:
                    raise IterableEnded
    def _go_integral(self, stop, **kwargs):
        for _ in range(stop):
            self.iterate(**kwargs)
    def _go_index(self, stop, index = None, **kwargs):
        if index is None:
            index = self._try_index(stop)
        stop += index.value if not self.indices.isnull else 0
        while index < stop:
            self.iterate(**kwargs)
    def _go_fn(self, stop, **kwargs):
        stop = self._try_convert(stop)
        stop = stop.allclose(self)
        while not stop:
            self.iterate(**kwargs)

    @_iterable_initialise_if_necessary()
    def run(self, *args, **kwargs):
        self.go(*args, **kwargs)

    @_iterable_initialise_if_necessary(post = True)
    def _out(self):
        return super()._out()
    @_iterable_changed_state
    def _load(self, arg, **kwargs):
        super()._load(arg, **kwargs)
    def load(self, arg, process = True, **kwargs):
        try:
            return super().load(arg, process = process, **kwargs)
        except IndexableLoadFail as e:
            if arg == 0:
                if not self.indices.iszero:
                    self.initialise()
                if not process:
                    return self.out()
            else:
                raise e

    def __getitem__(self, key):
        if type(key) is tuple:
            raise ValueError
        elif type(key) is slice:
            return Interval(self, key)
        else:
            return Stage(self, key)

class SpecFrame:
    def __init__(self, frame, targ, *targs):
        self.frame = frame
        if targ is None:
            targ = self.frame.indices.master.value
            self.index = targ
        else:
            self.index = None
        self.targs = tuple([targ, *targs])
        super().__init__()
    def compute(self):
        if self.index is None:
            self.frame.reach(*self.targs, silent = True)
            self.frame.store(silent = True)
            self.index = self.frame.indices.master.value
        else:
            self.frame.reach(self.index, silent = True)
    def _compute_wrap(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.compute()
            return func(self, *args, **kwargs)
        return wrapper

class Stage(SpecFrame, State):
    def __init__(self, arg, *targs):
        super().__init__(arg, *targs)
    @property
    @SpecFrame._compute_wrap
    def _vars(self):
        return self.frame.state.vars
    def __repr__(self):
        content = [self.frame.hashID, *(repr(t) for t in self.targs)]
        return type(self).__name__ + '(' + ', '.join(content) + ')'

class Interval(abcIterable):
    def __init__(self, frame, slicer):
        self.frame, self.slicer = frame, slicer
        super().__init__()
    def __iter__(self):
        return IntervalIterator(self.frame, self.slicer)
    # def __getitem__(self, key):
    #     raise Exception
    def __repr__(self):
        name = type(self).__name__
        content = self.frame.hashID, self.slicer
        return name + '(' + ', '.join(repr(o) for o in content) + ')'

class IntervalIterator(SpecFrame, abcIterator):
    def __init__(self, frame, slicer):
        self.start, self.step = slicer.start, slicer.step
        super().__init__(frame, self.start)
        self.stop = self.frame._get_stop_fn(slicer.stop)
        self.i = 0
        self.compute()
    def __next__(self):
        if self.stop:
            raise StopIteration
        else:
            self.frame.stride(self.step)
            return self.frame[None]
        #     print(repr(self.stop))
        #     self.frame.stride(self.step)
        #     self.i += 1
        #     return self.frame.indices
            # return Stage(
            #     self.frame,
            #     self.start,
            #     *[self.step for i in range(self.i - 1)]
            #     )
