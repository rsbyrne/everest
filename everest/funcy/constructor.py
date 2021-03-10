################################################################################

from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache
    )

import numbers as _numbers
from collections.abc import Iterable as _Iterable

from .exceptions import *

class _Fn:

    from .function import Function
    from . import base
    from . import derived
    from .derived import seq

    from .special import (
        null, nullflt, nullint,
        infint, ninfint, infflt, ninflt, inf, ninf,
        unk, unkflt, unkint,
        )

    def op(self, *args, opkey: str) -> derived.Op:
        return self.derived.Op(*args, opkey = opkey)

    def __call__(self, arg = None, /, *args, **kwargs) -> Function:
        try:
            if arg is None: # i.e. no args, hence not Derived
                return self.base.construct_base(arg, *args, **kwargs)
            elif arglen := len(args): # i.e. there are multiple args
                return self.derived.Group._construct(arg, *args, **kwargs)
            else: # i.e. only one arg
                if (argType := type(arg)) is tuple:
                    return self.derived.Group._construct(*arg, **kwargs)
                elif isinstance(arg, self.Function):
                    if len(kwargs):
                        raise ValueError("Kwargs not expected.")
                    return arg
                elif argType is dict:
                    return self.derived.Map._construct(
                        arg.keys(), arg.values()
                        )
                elif argType is set:
                    raise NotYetImplemented
                elif argType is slice:
                    return self.derived.slyce._construct(
                        arg.start, arg.stop, arg.step
                        )
                else:
                    return self.base.construct_base(arg, *args, **kwargs)
        except Exception as e:
            raise ConstructFailure(
                "Construct failed"
                f" with args = {(arg, *args)}, kwargs = {kwargs}; {e}"
                )

    def __getitem__(self, arg, /):
        if isinstance(arg, self.derived.Derived):
            if isinstance(arg, self.Function):
                if hasattr(arg, '_abstract'):
                    return self.seq.Algorithmic._construct(arg)
                else:
                    raise NotYetImplemented
            else:
                return self.seq.Discrete._construct(arg)
        elif type(arg) is slice:
            start, stop, step = arg.start, arg.stop, arg.step
            if isinstance(step, _numbers.Number):
                return self.seq.Regular._construct(start, stop, step)
            elif type(step) is str or step is None:
                if any(
                        isinstance(a, numbers.Integral)
                            for a in (start, stop)
                        ):
                    return self.seq.Shuffle._construct(
                        start, stop, step,
                        )
                else:
                    return self.seq.Continuum._construct(
                        start, stop, step,
                        )
            elif isinstance(step, self.seq.samplers.Sampler):
                return step._construct(start, stop)
            raise TypeError(
                "Could not understand 'step' input of type:", type(step)
                )
        elif isinstance(arg, _Iterable):
            return self.seq.Arbitrary._construct(*arg)
        else:
            raise TypeError(
                "Could not understand seq input of type:", type(arg)
                )

    @_cached_property
    def n(self):
        return self.seq.N()
    @_cached_property
    def unseq(self):
        return self.derived.UnSeq

Fn = _Fn()

################################################################################
