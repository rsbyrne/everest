###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import inspect as _inspect

import numpy as _np
from scipy.integrate import solve_ivp as _solve_ivp

from everest.ptolemaic.diict import Kwargs as _Kwargs
from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.schematic import Schematic as _Schematic

from everest.algebraic.brace import Brace as _Brace

from .traversable import Traversable as _Traversable


_Traverse = _Traversable._mrobase_Traverse


class ODESolver(metaclass=_Schematic):

    callfunc: _collabc.Callable

    defaultfreq = 0.005

    def __call__(self, subject, /):
        if isinstance(subject, _Traverse):
            return self.solve_traverse(subject)
        raise TypeError(type(subject))

    def solve_traverse(self, traverse, /):
        interval = traverse.interval
        t0, tf = interval.lower, interval.upper
        freq = getattr(interval, 'step', self.defaultfreq)
        return _solve_ivp(
            self.callfunc.__call__,
            (t0, tf),
            traverse.line.initial,
            t_eval=_np.linspace(t0, tf, round((tf - t0) / freq)),
            args=tuple(traverse.line.case),
            )


class ODEModel(metaclass=_Essence):

    @classmethod
    def __class_call__(cls, obj, /):
        return _Traversable(
            statespace = obj.__annotations__['state'],
            indexspace = obj.__annotations__['index'],
            casespace = _Brace[_Kwargs({
                name: parameter.annotation
                for name, parameter
                in tuple(_inspect.signature(obj).parameters.items())[2:]
                })],
            solver = ODESolver(obj),
            )


###############################################################################
###############################################################################


# import abc as _abc
# import inspect as _inspect
# import functools as _functools
# import types as _types

# from scipy.integrate import solve_ivp as _solve_ivp
# import numpy as _np

# from everest.incision import (
#     IncisionProtocol as _IncisionProtocol,
#     )

# from everest.ptolemaic.diict import Diict as _Diict
# from everest.ptolemaic.sprite import Sprite as _Sprite
# # from everest.ptolemaic.schema import Schema as _Schema
# from everest.ptolemaic.eidos import Eidos as _Schema
# from everest.ptolemaic.sig import Field as _Field
# from everest.ptolemaic.chora import (
#     ChainChora as _ChainChora,
#     Choric as _Choric,
#     Sampleable as _Sampleable,
#     )

# from everest.ptolemaic.fundaments.floatt import Floatt as _Floatt
# from everest.ptolemaic.fundaments.thing import Thing as _Thing


# class ODEModel(_Schema):

#     @classmethod
#     def decorate(meta, obj, /):
#         if isinstance(obj, type):
#             return meta(obj.__name__, (obj,), {})
#         signature = _inspect.signature(obj)
#         parameters = tuple(signature.parameters.values())
#         odeparams, odehints, odedefaults = {}, {}, {}
#         for name, parameter in tuple(signature.parameters.items())[2:]:
#             odeparams[name] = parameter
#             odehints[name] = parameter.annotation
#             odedefaults[name] = parameter.default
#         statespace = (
#             getattr(obj, '__annotations__', {})
#             .get('state', meta.BaseTyp.statespace)
#             )
#         metricspace = (
#             getattr(obj, '__annotations__', {})
#             .get('t', meta.BaseTyp.metricspace)
#             )
#         ns = dict(
#             odeparams=_types.MappingProxyType(odeparams),
#             odehints=_types.MappingProxyType(odehints),
#             odedefaults=_types.MappingProxyType(odedefaults),
#             statespace=statespace,
#             metricspace=metricspace,
#             __call__=staticmethod(obj),
#             __extra_annotations__=odehints,
#             _clsepitaph=meta.taphonomy(obj),
#             **odedefaults,
#             )
#         return meta(obj.__name__, (), ns)


# class ODEModelBase(_ChainChora, metaclass=ODEModel):


#     MROCLASSES = ('Line', 'Traverse', 'Stage')

#     statespace = _Thing.Oid.Brace
#     metricspace = _Floatt[0.:]

#     @classmethod
#     def _get_classchoras(cls, /):
#         out = super()._get_classchoras()
#         if (statespace := cls.statespace) is None:
#             return out
#         return out | dict(
#             state=cls.statespace,
#             metric=cls.metricspace,
#             )

#     @classmethod
#     def _get_classconstructors(cls, /):
#         return super()._get_classconstructors() | {
#             (False, False, True): cls.Traverse.construct_from_slyce
#             }

#     @property
#     def __incision_manager__(self, /):
#         return self.statespace

#     def __incise_retrieve__(self, incisor, /):
#         return self.Line(self, incisor)

#     @_abc.abstractmethod
#     def __call__(cls, /, *_, **__):
#         raise NotImplementedError


#     class Line(_ChainChora, metaclass=_Sprite):

#         basis: object
#         initial: object

#         def __incise_slyce__(self, incisor, /):
#             return self._ptolemaic_class__.owner.Traverse(self, incisor)

#         def __incise_retrieve__(self, incisor, /):
#             return self._ptolemaic_class__.owner.Stage(self, incisor)

#         @property
#         def __incision_manager__(self, /):
#             return self.basis.metricspace


#     class Traverse(_ChainChora, metaclass=_Sprite):

#         line: object
#         interval: object

#         defaultfreq = 0.005

#         @classmethod
#         def construct_from_slyce(cls, incisor, /):
#             itinc = iter(incisor.choras)
#             owner = cls.owner
#             basis = owner.instantiate(
#                 owner.sig.__incise_retrieve__(next(itinc).retrieve())
#                 )
#             line = _IncisionProtocol.RETRIEVE(basis)(next(itinc).retrieve())
#             return _IncisionProtocol.SLYCE(line)(next(itinc))

#         @property
#         def __incision_manager__(self, /):
#             return self.interval

#         def __incise_slyce__(self, incisor, /):
#             return self._ptolemaic_class__(self.line, incisor)

#         def __incise_retrieve__(self, incisor, /):
#             return self._ptolemaic_class__.owner.Stage(self.line, incisor)

#         def solve(self, /):
#             line = self.line
#             basis, interval = line.basis, self.interval
#             t0, tf = interval.lower, interval.upper
#             freq = getattr(interval, 'step', self.defaultfreq)
#             return _solve_ivp(
#                 basis.__call__,
#                 (t0, tf),
#                 line.initial,
#                 t_eval=_np.linspace(t0, tf, round((tf - t0) / freq)),
#                 args=tuple(getattr(basis, name) for name in basis.odeparams),
#                 )


#     class Stage(metaclass=_Sprite):

#         line: object
#         index: object

#         @property
#         def basis(self, /):
#             return self.line.basis


# class ODETraverse(_ChainChora, metaclass=_Schema):

#     line: _Field.POS[ODELine]
#     interval: _Field.POS[_Floatt.Oid.Closed[0.:]]
#     freq: _Field.KW[_Floatt[1e-12:]] = 0.005

#     @classmethod
#     def parameterise(cls, cache, /, *args, **kwargs):
#         bound = super().parameterise(cache, *args, **kwargs)
#         if isinstance((val := bound.arguments['interval']), tuple):
#             bound.arguments['interval'] = _Floatt.Oid.Closed(*val)
#         return bound

#     @property
#     def initial(self, /):
#         return self.line.initial

#     @property
#     def basis(self, /):
#         return self.line.basis

#     def solve(self, /):
#         basis, interval = self.basis, self.interval
#         ts = t0, tf = interval.lower, interval.upper
#         return _solve_ivp(
#             basis.__call__,
#             ts,
#             self.initial,
#             t_eval=_np.linspace(t0, tf, round((tf - t0) / self.freq)),
#             args=tuple(getattr(basis, name) for name in basis.odeparams),
#             )

#     @property
#     def __incision_manager__(self, /):
#         return self.interval

#     def __incise_slyce__(self, incisor, /):
#         return self.remake(interval=incisor)

#         @classmethod
#         def parameterise(cls, cache, /, *args, **kwargs):
#             bound = super().parameterise(cache, *args, **kwargs)
#             basis, initial = bound.arguments['basis'], bound.arguments['initial']
#             statespace = basis.statespace
#             if not initial in statespace:
#                 bound.arguments['initial'] = statespace[initial]
#             return bound
