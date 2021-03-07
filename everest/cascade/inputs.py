################################################################################

import inspect as _inspect
from types import FunctionType as _FunctionType, MethodType as _MethodType
from functools import cached_property as _cached_property

from .cascade import Cascade as _Cascade
from .hierarchy import Req as _Req

class Inputs(_Cascade):
    def __init__(self, source: _FunctionType, /, *args, **kwargs) -> None:
        if any(isinstance(source, t) for t in (_FunctionType, _MethodType)):
            self._Inputs_sig = _inspect.signature(source)
        elif isinstance(source, Inputs):
            self._Inputs_sig = source._Inputs_sig
        else:
            raise TypeError(
                f"Inputs source must be FunctionType or Inputs type,"
                f" not {type(source)}"
                )
        
        super().__init__(source, *args, **kwargs)
    @property
    def _Inputs_incomplete(self):
        return tuple(v.key for v in self.values() if isinstance(v, _Req))
    def _Inputs_unpack(self):
        if keys := self._Inputs_incomplete:
            raise ValueError(f"Missing required inputs: {keys}")
        sig = self._Inputs_sig
        params = sig.parameters
        args = []
        kwargs = dict()
        for key, val in self.items():
            if isinstance(val, _Req):
                raise ValueError(
                    f"Cannot unpack incomplete Cascade: {key}: {val.note}"
                    )
            try:
                param = params[key]
                if param.kind.value:
                    kwargs[key] = val
                else:
                    args.append(val)
            except KeyError:
                kwargs[key] = val
        self.__dict__['_Inputs_args'] = args
        self.__dict__['_Inputs_kwargs'] = kwargs
    @property
    def args(self):
        try:
            return self.__dict__['_Inputs_args']
        except KeyError:
            self._Inputs_unpack()
            return self.args
    @property
    def kwargs(self):
        try:
            return self.__dict__['_Inputs_kwargs']
        except KeyError:
            self._Inputs_unpack()
            return self.kwargs

################################################################################