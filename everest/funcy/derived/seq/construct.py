################################################################################

import numbers as _numbers
from collections.abc import Iterable as _Iterable

from . import _Derived
from .seq import Seq as _Seq
from .nvar import N as _N
from .algorithmic import Algorithmic as _Algorithmic
from .arbitrary import Arbitrary as _Arbitrary
from .continuous import Continuum as _Continuum
from .discrete import (
    Discrete as _Discrete,
    Regular as _Regular,
    Shuffle as _Shuffle,
    Procedural as _Procedural,
    )
from . import samplers as _samplers

from .exceptions import *

def construct_seq(arg = None, /) -> _Seq:
    if isinstance(arg, _Derived):
        if hasattr(arg, '_abstract'):
            return _Algorithmic._construct(arg)
        else:
            raise NotYetImplemented
    elif type(arg) is slice:
        start, stop, step = arg.start, arg.stop, arg.step
        if isinstance(step, _numbers.Number):
            return _Regular._construct(start, stop, step)
        elif type(step) is str or step is None:
            if any(
                    isinstance(a, _numbers.Integral)
                        for a in (start, stop)
                    ):
                return _Shuffle._construct(
                    start, stop, step,
                    )
            else:
                return _Continuum._construct(
                    start, stop, step,
                    )
        elif isinstance(step, _samplers.Sampler):
            return step._construct(start, stop)
        raise TypeError(
            "Could not understand 'step' input of type:", type(step)
            )
    elif isinstance(arg, _Iterable):
        return _Arbitrary._construct(*arg)
    else:
        raise TypeError(
            "Could not understand seq input of type:", type(arg)
            )

################################################################################