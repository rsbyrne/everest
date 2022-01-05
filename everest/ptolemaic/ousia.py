###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import itertools as _itertools

from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic
from everest.ptolemaic.essence import Essence as _Essence
# from everest.ptolemaic import ur as _ur


class ConcreteMeta(_Essence):

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
            taphonomy=basecls.taphonomy,
            __class_init__=lambda: None,
            __init__=basecls.__init__,
            __finish__=basecls.__finish__,
            )
        return meta.create_class(
            f"Concrete{basecls.__name__}",
            (basecls.ConcreteBase, _Ptolemaic, basecls),
            namespace,
            )

    @classmethod
    def process_bases(meta, bases, /):
        return bases

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):
        pass

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(type(cls), cls, *args, **kwargs)

    @property
    def _ptolemaic_class__(cls, /):
        return cls._basecls

    @property
    def __signature__(cls, /):
        return cls._ptolemaic_class__.__signature__


class Ousia(_Essence):

    @classmethod
    def concretemeta_namespace(meta, /):
        return {}

    @classmethod
    def _pleroma_init__(meta, /):
        super()._pleroma_init__()
        if not issubclass(meta, ConcreteMeta):
            meta.ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (ConcreteMeta, meta),
                meta.concretemeta_namespace(),
                )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.Concrete = cls.ConcreteMeta(cls)

    @property
    def __signature__(cls, /):
        return _inspect.signature(cls.Concrete.__init__)


class OusiaBase(metaclass=Ousia):

    MERGETUPLES = ('_req_slots__',)
    _req_slots__ = ()

    MROCLASSES = ('ConcreteBase',)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.Concrete(*args, **kwargs)

    def __init__(self, /):
        pass

    def __finish__(self, /):
        pass

    class ConcreteBase:

        __slots__ = ()

        @property
        def _ptolemaic_class__(self, /):
            return self.__class__._ptolemaic_class__


###############################################################################
###############################################################################


#         slots = tuple(sorted(set(_itertools.chain(
#             basecls._req_slots__, basecls._var_slots__
#             ))))

#     @property
#     def __call__(cls, /):
#         return cls.__class_call__

#     def create_ur_class(cls, name, /):
#         return cls.ConcreteMeta.create_class(
#             f"{cls.__name__}{name}",
#             (getattr(cls, f"{name}Base"), cls.Concrete),
#             {'__slots__': ()}
#             )

#         cls.Var = cls.create_ur_class('Var')
#         cls.Dat = cls.create_ur_class('Dat')

#     MERGETUPLES = ('_req_slots__', '_var_slots__')

#     _var_slots__ = ()

#     MROCLASSES = ('ConcreteBase', 'VarBase', 'DatBase')

#     @classmethod
#     def __class_call__(cls, /, *args, **kwargs):
#         constructor = cls.Var if cls._var_slots__ else cls.Dat
#         return constructor.__class_call__(*args, **kwargs)

#     class VarBase(_ur.Var):

#         __slots__ = ()

#         def __setattr__(self, name, value, /):
#             if name in self._var_slots__:
#                 self._alt_setattr__(name, value)
#             else:
#                 super().__setattr__(name, value)

#     class DatBase(_ur.Dat):

#         __slots__ = ()
