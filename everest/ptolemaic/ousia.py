###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.ptolemaic import (
    Ptolemaic as _Ptolemaic, PtolemaicBase as _PtolemaicBase
    )
from everest.ptolemaic.essence import Essence as _Essence


class ConcreteMeta(_Ptolemaic):

    @classmethod
    def _pleroma_construct(meta, basecls):
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if issubclass(type(basecls), ConcreteMeta):
            raise TypeError("Cannot subclass a Concrete type.")
        namespace = dict(
            __slots__=basecls._req_slots__,
            _basecls=basecls,
            __class_init__=lambda: None,
            )
        concretecls = meta.__new__(
            meta,
            f"Concrete{basecls.__name__}",
#             basecls.__name__,
            (basecls.ConcreteBase, _PtolemaicBase, basecls),
            namespace,
            )
        _abc.ABCMeta.__init__(meta, concretecls)
        return concretecls

    @property
    def __signature__(cls, /):
        return cls._ptolemaic_class__.__signature__

    @property
    def _class__ptolemaic_class__(cls, /):
        return cls._basecls


class Ousia(_Essence):

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
        if not issubclass(meta, ConcreteMeta):
            meta.ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (ConcreteMeta, meta),
                {},
                )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.Concrete = cls.ConcreteMeta(cls)

    @property
    def __call__(cls, /):
        return cls.Concrete


class OusiaBase(metaclass=Ousia):

    MERGETUPLES = ('_req_slots__',)
    _req_slots__ = ()

    MROCLASSES = ('ConcreteBase',)

    class ConcreteBase:
        ...


###############################################################################
###############################################################################
