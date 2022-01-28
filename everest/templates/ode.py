###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import functools as _functools
import types as _types

from scipy.integrate import solve_ivp as _solve_ivp
import numpy as _np

from everest.incision import ChainIncisable as _ChainIncisable

from everest.ptolemaic.schema import Schema as _Schema
from everest.ptolemaic.sig import Field as _Field
from everest.ptolemaic.thing import Thing as _Thing
from everest.ptolemaic.tuuple import Tuuple as _Tuuple
from everest.ptolemaic.floatt import (
    Floatt as _Floatt,
    FloattClosed as _FloattClosed,
    )
from everest.ptolemaic.chora import (
    Chora as _Chora,
    Sampleable as _Sampleable,
    )


class ODEModel(_Schema):

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
        statespace = (
            getattr(obj, '__annotations__', {})
            .get('state', _Tuuple)
            )
        ns = dict(
            odeparams=_types.MappingProxyType(odeparams),
            odehints=_types.MappingProxyType(odehints),
            odedefaults=_types.MappingProxyType(odedefaults),
            statespace=statespace,
            __call__=staticmethod(obj),
            __extra_annotations__=odehints,
            _clsepitaph=meta.taphonomy(obj),
            **odedefaults,
            )
        return meta(obj.__name__, (), ns)


class ODEModelBase(_Chora, metaclass=ODEModel):

    @property
    def __contains__(self, /):
        return self.statespace.__contains__

    @_abc.abstractmethod
    def __call__(self, t, state: _Thing, /):
        raise NotImplementedError

    @property
    def line(self):
        return _functools.partial(ODELine, self)

    def traverse(self, initial, interval, /):
        return self.line(initial).traverse(interval)

    class __incision_manager__(_Sampleable):

        def bounds_slyce_open(self, incisor: (object, type(None)), /):
            return self.bound.line(incisor.lower)

        def bounds_slyce_closed(self, incisor: (object, object), /):
            return self.bound.traverse(incisor.lower, (0., incisor.upper))


class ODELine(_Chora, metaclass=_Schema):

    basis: _Field.POS[ODEModelBase]
    initial: _Field.POS[_Thing]

    @classmethod
    def check_params(cls, params, /):
        super().check_params(params)
        if params.initial not in params.basis:
            raise cls.paramexc(params.initial)

    @property
    def traverse(self, /):
        return _functools.partial(ODETraverse, self)

    class __incision_manager__(_Sampleable):

        def bounds_slyce_closed(self, incisor: (object, object), /):
            return self.traverse(incisor.lower, incisor.upper)


class ODETraverse(_ChainIncisable, metaclass=_Schema):

    line: _Field.POS[ODELine]
    interval: _Field.POS[_FloattClosed]
    freq: _Field.KW[_Floatt[1e-12:]] = 0.01

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = super().parameterise(cache, *args, **kwargs)
        if isinstance((val := bound.arguments['interval']), tuple):
            bound.arguments['interval'] = _FloattClosed(*val)
        return bound

    @property
    def initial(self, /):
        return self.line.initial

    @property
    def basis(self, /):
        return self.line.basis

    def solve(self, /):
        basis, interval = self.basis, self.interval
        ts = t0, tf = interval.lower, interval.upper
        return _solve_ivp(
            basis.__call__,
            ts,
            self.initial,
            t_eval=_np.linspace(t0, tf, round((tf - t0) / self.freq)),
            args=tuple(getattr(basis, name) for name in basis.odeparams),
            )

    @property
    def __incision_manager__(self, /):
        return self.interval

    def __incise_slyce__(self, incisor, /):
        return self.remake(interval=incisor)


###############################################################################
###############################################################################
