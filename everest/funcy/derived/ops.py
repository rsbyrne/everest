################################################################################

import builtins as _builtins
import operator as _operator
import math as _math
from functools import cached_property as _cached_property

from . import _generic, _Function, _Thing
from .derived import Derived as _Derived
from .group import Group as _Group
from .map import Map as _Map

class _Ops(_Derived):
    ...

class Call(_Ops):
    def __init__(self,
            callObj: callable,
            callArgs: _generic.FuncyStruct = (),
            callKwargs: _generic.FuncyMapping = (),
            /,
            **kwargs,
            ) -> None:           
        if not isinstance(callArgs, _Function):
            if not len(callArgs): callArgs = _Thing(tuple())
            else: callArgs = _Group(*callArgs)
        if not isinstance(callKwargs, _Function):
            if not len(callKwargs): callKwargs = _Thing(dict())
            else: callKwargs = _Map(callKwargs.keys(), callKwargs.values())
        super().__init__(callObj, callArgs, callKwargs, **kwargs)
    def _evaluate(self, terms):
        obj, args, kwargs = terms
        return obj(*args, **kwargs)

class _Get(_Ops):
    def __init__(self,
            getObj: object,
            getArg: object,
            /,
            **kwargs,
            ) -> None:
        if not isinstance(getObj, _Function):
            getObj = _Thing(getObj)
        if not isinstance(getArg, _Function):
            getArg = _Thing(getArg)
        super().__init__(getObj, getArg, **kwargs)
class GetItem(_Get):
    def _evaluate(self, terms):
        obj, arg = terms
        return obj[arg]
class GetAttr(_Get):
    def _evaluate(self, terms):
        obj, arg = terms
        return getattr(obj, arg)

class Op(_Ops):
    __slots__ = ('opfn', 'opkwargs')
    def __init__(self, *args, opkey: str, **kwargs):
        opfn = None
        for source in (_builtins, _operator, _math):
            try:
                opfn = getattr(source, opkey)
                break
            except AttributeError:
                pass
        if opfn is None:
            raise AttributeError(opkey)
        kwargs['opkey'] = opkey
        super().__init__(*args, **kwargs)
        self.opkwargs = {k: v for k, v in self.kwargs.items() if not k == 'opkey'}
        self.opfn = opfn
    def _evaluate(self, terms):
        return self.opfn(*terms, **self.opkwargs)

################################################################################