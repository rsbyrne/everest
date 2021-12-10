###############################################################################
''''''
###############################################################################


import functools as _functools
import weakref as _weakref
import abc as _abc
import itertools as _itertools
import pickle as _pickle
import inspect as _inspect

from everest.utilities import caching as _caching, switch as _switch
from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
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
        Concrete = cls.Concrete = cls.ConcreteMeta(cls)
        cls.create_object = _functools.partial(Concrete.__new__, Concrete)


class OusiaBase(metaclass=Ousia):
    '''
    The basetype of all Ousia instances.
    '''

    _ptolemaic_mergetuples__ = ('_req_slots__',)
    _req_slots__ = ('params',)

    ### What actually happens when the class is called:

    @classmethod
    def get_signature(cls, /):
        return (
            (sig := _inspect.signature(cls.__init__))
            .replace(
                parameters=tuple(sig.parameters.values())[1:],
                return_annotation=cls,
                )
            )

    def initialise(self, /):
        params = self.params
        self.__init__(*params.args, **params.kwargs)

    @classmethod
    def construct(cls, callsig, /):
        obj = cls.create_object()
        obj.params = callsig
        obj._softcache = {}
        obj._weakcache = _weakref.WeakValueDictionary()
        obj.initialise()
        obj.freezeattr = True
        return obj

    ### Epitaph support:

    @classmethod
    def get_instance_epitaph(cls, callsig, /):
        cls = cls._ptolemaic_class__
        return cls.clstaphonomy.custom_epitaph(
            "$a[$b]",
            dict(a=cls, b=callsig),
            )

    ### Defining special behaviours for the concrete subclass:

    def get_epitaph(self, /):
        return self.get_instance_epitaph(self.params)

    def _repr(self, /):
        args, kwargs = (params := self.params).args, params.kwargs
        return ', '.join(_itertools.chain(
            map(repr, args),
            map(
                '='.join,
                zip(map(str, kwargs), map(repr, kwargs.values()))
                ),
            ))


###############################################################################
###############################################################################
