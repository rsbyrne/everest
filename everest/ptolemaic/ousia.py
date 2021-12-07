###############################################################################
''''''
###############################################################################


import functools as _functools
import weakref as _weakref
import abc as _abc
import itertools as _itertools
import pickle as _pickle
import inspect as _inspect

from everest import classtools as _classtools
from everest.utilities import caching as _caching, switch as _switch
from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic.tekton import Tekton as _Tekton
from everest.ptolemaic.corporeal import Corporeal as _Corporeal


class Ousia(_Tekton):
    '''
    The metaclass of all ptolemaic types that can be instantiated.
    All instances of `Ousia` types are instances of `Ptolemaic` by definition.
    '''

    ### Defining the parent class of all Ousia instance instances:

    class ConcreteMetaBase(_Corporeal):

        @property
        def epitaph(cls, /):
            return cls._ptolemaic_class__.epitaph

    ### Implementing the class concretion mechanism:

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
        meta.premade = _weakref.WeakValueDictionary()
        if not issubclass(meta, meta.ConcreteMetaBase):
            meta.ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (meta.ConcreteMetaBase, meta),
                dict(metabasecls=meta),
                )

    def _ptolemaic_concrete_slots__(cls, /):
        return cls._req_slots__

    def _ptolemaic_concrete_namespace__(cls, /):
        return dict(
            _basecls=cls,
            __slots__=cls._ptolemaic_concrete_slots__(),
            __class_init__=lambda: None,
            )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.Concrete = cls.ConcreteMeta(cls)
        cls.create_object = _functools.partial(cls.__new__, cls.Concrete)


class OusiaBase(metaclass=Ousia):
    '''
    The basetype of all Ousia instances.
    '''

    _ptolemaic_mergetuples__ = ('_req_slots__',)
    _req_slots__ = (
        '_softcache', '_weakcache', 'params', '__weakref__', '_freezeattr',
        )
    _ptolemaic_mroclasses__ = ('ConcreteBase',)

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
        return cls.taphonomy.custom_epitaph("$a[$b]", dict(a=cls, b=callsig))

    ### Defining special behaviours for the concrete subclass:

    class ConcreteBase(metaclass=_Corporeal):
        '''The base class for this class's `Concrete` subclass.'''

        ### Implementing serialisation of instances:

        @property
        @_caching.soft_cache()
        def epitaph(self, /):
            return self.get_instance_epitaph(self.params)

        ### Defining some aliases:

        @property
        def metacls(self, /):
            return self._ptolemaic_class__.metacls

        @property
        def taphonomy(self, /):
            return self.metacls.taphonomy

        @property
        def hexcode(self, /):
            return self.epitaph.hexcode

        @property
        def hashint(self, /):
            return self.epitaph.hashint

        @property
        def hashID(self, /):
            return self.epitaph.hashID

        ### Defining ways that class instances can be represented:

        def __hash__(self, /):
            return self.hashint

        @classmethod
        def __class_repr__(cls, /):
            return cls.__class__.__qualname__

        @classmethod
        def __class_str__(cls, /):
            return cls._ptolemaic_class__.__class_str__()

        def _repr(self, /):
            args, kwargs = (params := self.params).args, params.kwargs
            return ', '.join(_itertools.chain(
                map(repr, args),
                map(
                    '='.join,
                    zip(map(str, kwargs), map(repr, kwargs.values()))
                    ),
                ))

        @_caching.soft_cache()
        def __repr__(self, /):
            content = f"({rep})" if (rep := self._repr()) else ''
            return f"<{self.__class__}{content}>"


###############################################################################
###############################################################################
