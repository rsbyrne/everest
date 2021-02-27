################################################################################

from collections import OrderedDict
from collections.abc import Sequence
from numbers import Number
from functools import cached_property, lru_cache

import numpy as np

from .exceptions import *

class _Fn:
    @cached_property
    def op(self):
        from .ops import ops
        return ops
    # @cached_property
    # def elementop(self):
    #     from .ops import elementops
    #     return elementops
    # @cached_property
    # def seqop(self):
    #     from .ops import seqops
    #     return seqops
    @cached_property
    def base(self):
        from .base import Function
        return Function
    @cached_property
    def var(self):
        from .variable import Variable
        return Variable
    @cached_property
    def slot(self):
        from .slot import Slot
        return Slot
    @cached_property
    def group(self):
        from .group import Group
        return Group
    @cached_property
    def exc(self):
        from ._trier import Trier
        return Trier
    @cached_property
    def seq(self):
        from .seq.constructor import SeqConstructor
        return SeqConstructor()
    @cached_property
    def unseq(self):
        from .unseq import UnSeq
        return UnSeq
    @cached_property
    def thing(self):
        from .thing import Thing
        return Thing
    @cached_property
    def map(self):
        from .map import Map
        return Map
    @cached_property
    def inf(self):
        from .special import inf
        return inf
    @cached_property
    def ninf(self):
        from .special import ninf
        return ninf
    @cached_property
    def null(self):
        from .special import null
        return null
    @cached_property
    def n(self):
        from .seq.nvar import N
        return N()
    @cached_property
    def slyce(self):
        from .slyce import Slyce
        return Slyce
    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            return self.slot(**kwargs)
        elif len(args) > 1:
            return self.group(*args, **kwargs)
        else: # hence len(args) == 1
            arg = args[0]
            if len(kwargs) == 0 and isinstance(arg, self.base):
                return arg
            elif type(arg) is tuple:
                return self.group(*arg)
            elif type(arg) is dict:
                return self.map(arg.keys(), arg.values())
            elif type(arg) is set:
                raise NotYetImplemented
            elif type(arg) is slice:
                return self.slyce(arg.start, arg.stop, arg.step)
            elif any(isinstance(arg, typ) for typ in {
                    Number,
                    np.ndarray,
                    np.generic,
                    str,
                    Sequence,
                    }):
                return self.var.construct_variable(*args, **kwargs)
            else:
                return self.thing(arg, **kwargs)
    def __getitem__(self, arg, **kwargs):
        return self.seq(arg, **kwargs)
    @lru_cache
    def __getattr__(self, key):
        for sk in ('op', 'seq'):
            source = getattr(self, sk)
            try:
                return getattr(source, key)
            except AttributeError:
                pass
        raise AttributeError
Fn = _Fn()

################################################################################
