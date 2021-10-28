###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import more_itertools as _mitertools
import inspect as _inspect
import operator as _operator

from . import _utilities

from .pleroma import Pleroma as _Pleroma


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


class Essence(_abc.ABCMeta, metaclass=_Pleroma):

    _ptolemaic_mergetuples__ = ()
    _ptolemaic_mergedicts__ = ()

    @classmethod
    def __meta_init__(meta, /):
        pass

    @classmethod
    def _customise_namespace(meta, namespace, /):
        namespace['metacls'] = meta
        if '__slots__' not in namespace:
            namespace['__slots__'] = ()
        return namespace

    def __new__(meta, name, bases, namespace, /):
        namespace = meta._customise_namespace(namespace)
        return super().__new__(meta, name, bases, namespace)

    @staticmethod
    def _gather_names(bases, name, methcall, /):
        return ordered_set(_itertools.chain.from_iterable(
            methcall(getattr(base, name))
            for base in bases if hasattr(base, name)
            ))

    def _merge_names(cls, name, /, *, mergetyp=tuple, itermeth='__iter__'):
        methcall = _operator.methodcaller(itermeth)
        meta = type(cls)
        merged = []
        merged.extend(cls._gather_names(
            (meta, *meta.__bases__),
            name,
            methcall,
            ))
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
        cls.__class_init__()

    def __class_init__(cls, /):
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

    @property
    def __signature__(cls, /):
        return _inspect.signature(cls.__init__)

    @classmethod
    def __prepare__(meta, name, bases, /):
        return dict()

    def _cls_repr(cls, /):
        return super().__repr__()

    def __repr__(cls, /):
        return cls._cls_repr()

    def construct(cls, /, *args, **kwargs):
        raise NotImplementedError

    def __call__(cls, /, *args, **kwargs):
        return cls.construct(*args, **kwargs)


###############################################################################
###############################################################################
