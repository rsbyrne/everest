###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import functools as _functools
import types as _types

from scipy.integrate import solve_ivp as _solve_ivp
import numpy as _np

from everest.ptolemaic.schema import Schema as _Schema
from everest.ptolemaic.thing import Thing as _Thing
from everest.ptolemaic.tuuple import Tuuple as _Tuuple
from everest.ptolemaic.floatt import Floatt as _Floatt
from everest.ptolemaic.chora import Sampleable


class ODEModel(_Schema):

    def __class_deep_init__(cls, /, *args, **kwargs):
        super().__class_deep_init__(*args, **kwargs)
        cls.statespace = (
            getattr(cls.__call__, '__annotations__', {})
            .get('return', _Tuuple)
            )

    @classmethod
    def decorate(meta, obj, /):
        if isinstance(obj, type):
            return meta(obj.__name__, (obj,), {})
        signature = _inspect.signature(obj)
        parameters = tuple(signature.parameters.values())
        odeparams, odehints, odedefaults = {}, {}, {}
        for name, parameter in tuple(signature.parameters.items())[2:]:
            odeparams[name] = parameter
            odehints[name] = parameter.annotation
            odedefaults[name] = parameter.default
        ns = dict(
            odeparams=_types.MappingProxyType(odeparams),
            odehints=_types.MappingProxyType(odehints),
            odedefaults=_types.MappingProxyType(odedefaults),
            __call__=staticmethod(obj),
            __extra_annotations__=odehints,
            _clsepitaph=meta.taphonomy(obj),
            **odedefaults,
            )
        return meta(obj.__name__, (), ns)


class ODEModelBase(metaclass=ODEModel):

    @property
    def __contains__(self, /):
        return self.statespace.__contains__

    @_abc.abstractmethod
    def __call__(self, t, state: _Thing, /):
        raise NotImplementedError


class ODELine(metaclass=_Schema):

    basis: ODEModelBase
    initial: _Thing

    @classmethod
    def check_params(cls, params, /):
        super().check_params(params)
        if params.initial not in params.basis:
            raise cls.paramexc(params.initial)


class ODETraverse(metaclass=_Schema):

    line: ODELine
    t0: _Floatt[0.:]
    tf: _Floatt[1e-12:]
    freq: _Floatt[1e-12:] = 0.1

    @classmethod
    def check_params(cls, params, /):
        super().check_params(params)
        if params.tf <= params.t0:
            raise cls.paramexc(params.tf, params.t0)

    def solve(self, /):
        basis = self.line.basis
        func = basis.__call__
        args = tuple(getattr(basis, name) for name in basis.odeparams)
        print(args)
        t0, tf = self.t0, self.tf
        duration = tf - t0
        return _solve_ivp(
            func,
            (self.t0, self.tf),
            self.line.initial,
            t_eval=_np.linspace(t0, tf, round(duration / self.freq)),
            args=args,
            )


###############################################################################
###############################################################################
