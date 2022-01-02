###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.ptolemaic.ptolemaic import (
    Ptolemaic as _Ptolemaic,
    PtolemaicBase as _PtolemaicBase,
    )


class Corporealiser(_Ptolemaic):

    @classmethod
    def _pleroma_construct(meta, arg0, /, *args):
        if args:
            return super()._pleroma_construct(arg0, *args)
        basecls = arg0
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if isinstance(basecls, Corporealiser):
            raise TypeError("Cannot subclass a Concrete type.")
        namespace = dict(
            __slots__=basecls._req_slots__,
            _basecls=basecls,
            __class_init__=lambda: None,
            )
        return meta._create_class(
            f"Concrete{basecls.__name__}",
            (basecls, _PtolemaicBase),
            namespace,
            )

    @property
    def __signature__(cls, /):
        return cls._ptolemaic_class__.__signature__

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(type(cls), cls, *args, **kwargs)

    @property
    def _ptolemaic_class__(cls, /):
        return cls._basecls


# class Incorporable(_abc.ABC):

#     @_abc.abstractmethod
#     @classmethod
#     def _ptolemaic_concrete_namespace__(c


###############################################################################
###############################################################################
