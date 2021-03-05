################################################################################

from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache
    )

from .exceptions import *

class _Fn:

    from .function import Function
    from . import base
    from . import derived
    from .ops import ops, seqops

    from .special import (
        null, nullflt, nullint,
        infint, ninfint, infflt, ninflt, inf, ninf,
        unk, unkflt, unkint,
        )

    def __call__(self, arg = None, /, *args, **kwargs) -> Function:
        try:
            if arg is None: # i.e. no args, hence not Derived
                return self.base.construct_base(arg, *args, **kwargs)
            elif arglen := len(args): # i.e. there are multiple args
                return self.derived.Group(arg, *args, **kwargs)
            else: # i.e. only one arg
                if (argType := type(arg)) is tuple:
                    return self.derived.Group(*arg, **kwargs)
                elif isinstance(arg, self.Function):
                    if len(kwargs):
                        raise ValueError("Kwargs not expected.")
                    return arg
                elif argType is dict:
                    return self.derived.Map(arg.keys(), arg.values())
                elif argType is set:
                    raise NotYetImplemented
                elif argType is slice:
                    return self.derived.slyce(arg.start, arg.stop, arg.step)
                else:
                    return self.base.construct_base(arg, *args, **kwargs)
        except Exception as e:
            raise ConstructFailure(
                "Construct failed"
                f" with args = {(arg, *args)}, kwargs = {kwargs}; {e}"
                )

    def __getitem__(self, arg, **kwargs):
        return self.seq(arg, **kwargs)

    @_cached_property
    def seq(self):
        return self.derived.seq.SeqConstructor()
    @_cached_property
    def n(self):
        return self.derived.seq.N()
    @_cached_property
    def unseq(self):
        from .derived import UnSeq
        return UnSeq

Fn = _Fn()

################################################################################
