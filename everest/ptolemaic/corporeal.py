###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import caching as _caching

from everest.ptolemaic.pleroma import Pleromatic as _Pleromatic
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


class Corporeal(_Pleromatic):

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
        if isinstance(basecls, basecls.ConcreteMetaBase):
            raise TypeError("Cannot subclass a Concrete type.")
        out = _abc.ABCMeta.__call__(
            meta,
            f"Concrete{basecls.__name__}",
            (basecls.ConcreteBase, basecls),
            basecls._ptolemaic_concrete_namespace__(),
            )
        out.clsfreezeattr = True
        return out

    @property
    def __signature__(cls, /):
        return cls._ptolemaic_class__.__signature__

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(cls, *args, **kwargs)

    @property
    def _ptolemaic_class__(cls, /):
        return cls._basecls


class CorporealBase(_Ptolemaic, metaclass=Corporeal):

    ### Rich comparisons to support ordering of objects:

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)

    ### Representations:

    @classmethod
    def __class_repr__(cls, /):
        return cls.__class__.__qualname__

    @classmethod
    def __class_str__(cls, /):
        return cls._ptolemaic_class__.__class_str__()

    def _repr(self, /):
        return str(hash(self))

    @_caching.soft_cache()
    def __repr__(self, /):
        content = f"({rep})" if (rep := self._repr()) else ''
        return f"<{self.__class__}{content}>"


# class Incorporable(_abc.ABC):

#     @_abc.abstractmethod
#     @classmethod
#     def _ptolemaic_concrete_namespace__(c


###############################################################################
###############################################################################
