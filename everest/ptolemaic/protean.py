###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import weakref as _weakref

from everest.utilities import caching as _caching, reseed as _reseed

from everest.ptolemaic.essence import Essence
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic.corporeal import Corporeal as _Corporeal


class Protean(Essence):

    class ConcreteMetaBase(_Corporeal):
        ...

    ### Implementing the class concretion mechanism:

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
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

    ### What happens when the class is called:

    def construct(cls, /, *_, **__):
        raise NotImplementedError

    def __class_call__(cls, /, *args, **kwargs):
        return cls.construct(*args, **kwargs)


class ProteanBase(_Ptolemaic, metaclass=Protean):

    _ptolemaic_mergetuples__ = ('_req_slots__', '_var_slots__')
    _req_slots__ = (
        '_softcache', '_weakcache', '__weakref__', '_freezeattr', 'hashint'
        )
    _ptolemaic_mroclasses__ = ('ConcreteBase',)

    def __setattr__(self, key, val, /):
        if key in self._var_slots__:
            self._alt_setattr__(key, val)
        else:
            super().__setattr__(key, val)

    ### What happens when the class is called:

    def initialise(self, /, *args, **kwargs):
        self.__init__(*args, **kwargs)

    @classmethod
    def construct(cls, /, *args, **kwargs):
        obj = cls.create_object()
        obj._softcache = {}
        obj._weakcache = _weakref.WeakValueDictionary()
        obj.hashint = _reseed.rdigits()
        obj.initialise(*args, **kwargs)
        obj.freezeattr = True
        return obj

    ### Defining special behaviours for the concrete subclass:

    class ConcreteBase(metaclass=_Corporeal):

        def __hash__(self, /):
            return self.hashint


###############################################################################
###############################################################################
