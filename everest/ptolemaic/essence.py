###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import itertools as _itertools
import more_itertools as _mitertools
import inspect as _inspect
import operator as _operator

from everest import utilities as _utilities
from everest.ptolemaic.pleroma import Pleroma as _Pleroma


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    @classmethod
    def _pleroma_init__(meta, /):
        pass

    @classmethod
    def __prepare__(meta, name, bases, /, *args, **kwargs):
        return dict()

    @property
    def __call__(cls):
        raise NotImplementedError

    def get_classproxy(cls, /):
        return cls

    @property
    def classproxy(cls, /):
        return cls.get_classproxy()

    def __repr__(cls, /):
        return cls.__class_repr__()

    def __instancecheck__(cls, arg, /):
        return cls._ptolemaic_isinstance__(arg)

#     def __subclasscheck__(cls, arg, /):
#         return cls._ptolemaic_issubclass__(arg)

    def __contains__(cls, arg, /):
        return cls._ptolemaic_contains__(arg)

    def __getitem__(cls, arg, /):
        return cls._ptolemaic_getitem__(arg)

    class BASETYP(_abc.ABC):

        __slots__ = ()

        _ptolemaic_mergetuples__ = ()
        _ptolemaic_mergedicts__ = ()

        @classmethod
        def __class_init__(cls, /):
            pass

        @classmethod
        def __class_repr__(cls, /):
            return cls.__qualname__

        @classmethod
        def _ptolemaic_isinstance__(cls, arg, /):
            return issubclass(type(arg), cls)

#         @classmethod
#         def _ptolemaic_issubclass__(cls, arg, /):
#             return _abc.ABCMeta.__subclasscheck__(cls, arg)

        @classmethod
        def _ptolemaic_contains__(cls, arg, /):
            raise NotImplementedError

        @classmethod
        def _ptolemaic_getitem__(cls, arg, /):
            raise NotImplementedError

    @classmethod
    def process_bases(meta, bases):
        if tuple(filter((basetyp := meta.BASETYP).__subclasscheck__, bases)):
            return bases
        return (*bases, basetyp)

    def __new__(meta, name, bases, namespace, /, *args, **kwargs):
        bases = meta.process_bases(bases)
        namespace['metacls'] = meta
        namespace['__slots__'] = ()
        return super().__new__(meta, name, bases, namespace, *args, **kwargs)

    @staticmethod
    def _gather_names(bases, name, methcall, /):
        return ordered_set(_itertools.chain.from_iterable(
            methcall(getattr(base, name))
            for base in bases if hasattr(base, name)
            ))

    def _merge_names(cls, name, /, *, mergetyp=tuple, itermeth='__iter__'):
        methcall = _operator.methodcaller(itermeth)
        merged = []
        merged.extend(cls._gather_names(cls.__bases__, name, methcall))
        if name in cls.__dict__:
            merged.extend(ordered_set(methcall(getattr(cls, name))))
        merged = ordered_set(merged)
        setattr(cls, name, mergetyp(merged))

    def _merge_names_all(cls, overname, /, **kwargs):
        cls._merge_names(overname)
        for name in getattr(cls, overname):
            cls._merge_names(name, **kwargs)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = dict()
        cls._merge_names('_ptolemaic_mergetuples_')
        cls._merge_names('_ptolemaic_mergedicts__')
        cls._merge_names_all(
            '_ptolemaic_mergetuples__'
            )
        cls._merge_names_all(
            '_ptolemaic_mergedicts__',
            mergetyp=_utilities.FrozenMap,
            itermeth='items',
            )


###############################################################################
###############################################################################
