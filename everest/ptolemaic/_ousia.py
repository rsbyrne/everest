###############################################################################
''''''
###############################################################################


import functools as _functools
import weakref as _weakref
import abc as _abc
import itertools as _itertools
import pickle as _pickle
import inspect as _inspect
import types as _types

from everest.utilities import (
    caching as _caching, switch as _switch,
    format_argskwargs as _format_argskwargs,
    )
from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic.params import Sig as _Sig
from everest.ptolemaic.tekton import Tekton as _Tekton
from everest.ptolemaic.corporealiser import Corporealiser as _Corporealiser


class Ousia(_Tekton):
    '''
    The metaclass of all ptolemaic types that can be instantiated.
    All instances of `Ousia` types are instances of `Ptolemaic` by definition.
    '''

    ### Implementing the class concretion mechanism:

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
        if not issubclass(meta, _Corporealiser):
            meta.ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (_Corporealiser, meta),
                dict(metabasecls=meta),
                )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.Concrete = cls.ConcreteMeta(cls)

    def get_signature(cls, /):
        return _Sig(
            (sig := _inspect.signature(cls.Concrete.__init__))
            .replace(
                parameters=tuple(sig.parameters.values())[1:],
                return_annotation=cls,
                )
            )


class OusiaBase(metaclass=Ousia):
    '''
    The basetype of all Ousia instances.
    '''

    MERGETUPLES = ('_req_slots__',)
    _req_slots__ = ('params',)

    ### What actually happens when the class is called:

    @classmethod
    def create_object(cls, /):
        conc = cls.Concrete
        return conc.__new__(conc)

    @classmethod
    def instantiate(cls, params, /):
        obj = cls.create_object()
        obj.params = params
        obj.__init__(*params.args, **params.kwargs)
        return obj

    @classmethod
    def construct(cls, params, /):
        obj = cls.instantiate(params)
        obj.__finish__()
        return obj

    def get_epitaph(self, /):
        params = self.params
        return self.taphonomy.callsig_epitaph(
            self._ptolemaic_class__, *params.args, **params.kwargs
            )

    def _repr(self, /):
        return str(self.params)


###############################################################################
###############################################################################
