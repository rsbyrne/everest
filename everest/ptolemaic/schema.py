###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator

from everest.utilities import caching as _caching

from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.params import Param as _Param, Sig as _Sig


class Schema(_Ousia):
    '''
    The metaclass of all Schema classes.
    '''

    def _collect_params(cls, /):
        params = dict()
        for name, note in cls.__annotations__.items():
            if note is _Param:
                note = note()
            elif not isinstance(note, _Param):
                note = _Param()
            value = (
                cls.__dict__[name] if name in cls.__dict__
                else NotImplemented
                )
            bound = note(name=name, value=value)
            deq = params.setdefault(name, _collections.deque())
            deq.append(bound)
        for base in cls.__bases__:
            if not isinstance(base, Schema):
                continue
            for name, param in base.sig.items():
                deq = params.setdefault(name, _collections.deque())
                deq.append(param)
        return (
            _functools.reduce(_operator.getitem, reversed(deq))
            for deq in params.values()
            )

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        cls.sig = cls.get_signature()
        super().__init__(*args, **kwargs)

    @property
    def __signature__(cls, /):
        return cls.sig.signature

    def _ptolemaic_concrete_namespace__(cls, /):
        return {
            **super()._ptolemaic_concrete_namespace__(),
            **cls.sig,
            }


class SchemaBase(metaclass=Schema):

    __slots__ = ()

    _req_slots__ = ('params',)

    @classmethod
    def get_signature(cls, /):
        return _Sig(*cls._collect_params())

    def initialise(self, params, /):
        self.params = params
        self._repr = self.hexcode
        self.__init__()

    @classmethod
    def construct(cls, /, *args, **kwargs):
        cls.parameterise(registrar := cls.registrar, *args, **kwargs)
        registrar.check()
        params = cls.sig(*registrar.args, **registrar.kwargs)
        return cls.instantiate(params)

    ### Epitaph support:

    @classmethod
    def get_instance_epitaph(cls, params, /):
        return cls.taphonomy.custom_epitaph(
            "{0}.instantiate({1})", (cls, params)
            )


###############################################################################
###############################################################################
