###############################################################################
''''''
###############################################################################


import itertools as _itertools
import more_itertools as _mitertools
import weakref as _weakref
import operator as _operator

from everest.utilities import (
    caching as _caching,
    FrozenMap as _FrozenMap,
    )

from everest.ptolemaic import pleroma as _pleroma
from everest.ptolemaic.ptolemaic import Ptolemaic as _Ptolemaic


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


class Essence(_pleroma.Pleromatic):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Implementing mergetuples and mergedicts:

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

    ### Implementing mroclasses:

    def _add_mroclass(cls, name: str, /):
        adjname = f'_mroclassbase_{name}__'
        fusename = f'_mroclassfused_{name}__'
        if name in cls.__dict__:
            setattr(cls, adjname, cls.__dict__[name])
        inhclasses = []
        for mcls in cls.__mro__:
            searchname = adjname if isinstance(mcls, Essence) else name
            if searchname in mcls.__dict__:
                if not (inhcls := mcls.__dict__[searchname]) in inhclasses:
                    inhclasses.append(inhcls)
        inhclasses = tuple(inhclasses)
        if len(inhclasses) == 1:
            mroclass = inhclasses[0]
        else:
            mroclass = type(name, inhclasses, {'__slots__':()})
        setattr(cls, fusename, mroclass)
        setattr(cls, name, mroclass)

    def _add_mroclasses(cls, /):
        for name in cls._ptolemaic_mroclasses__:
            cls._add_mroclass(name)

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._cls_softcache = {}
        cls._cls_weakcache = _weakref.WeakValueDictionary()
        clsdct = cls.__dict__
        if (annokey := '__annotations__') in clsdct:
            anno = clsdct[annokey]
        else:
            setattr(cls, annokey, anno := {})
        if (extkey := '_extra_annotations__') in clsdct:
            anno.update(clsdct[extkey])
        setattr(cls, annokey, _FrozenMap(anno))
        cls._merge_names('_ptolemaic_mergetuples_')
        cls._merge_names('_ptolemaic_mergedicts__')
        cls._merge_names_all(
            '_ptolemaic_mergetuples__'
            )
        cls._merge_names_all(
            '_ptolemaic_mergedicts__',
            mergetyp=_FrozenMap,
            itermeth='items',
            )
        cls._add_mroclasses()

    ### What happens when the class is called:

    def __class_call__(cls, /, *_, **__):
        raise NotImplementedError

    @property
    def __call__(cls, /):
        return cls._ptolemaic_class__.__class_call__

    ### Defining aliases and representations for classes:

    def __class_repr__(cls, /):
        raise NotImplementedError

    def __class_str__(cls, /):
        raise NotImplementedError

    def __repr__(cls, /):
        return cls.__class_repr__()

    def __str__(cls, /):
        return cls.__class_str__()

    @property
    def _ptolemaic_class__(cls, /):
        return cls

    @property
    def metacls(cls, /):
        return type(cls._ptolemaic_class__)

    @property
    def taphonomy(cls, /):
        return cls.metacls.taphonomy

    @property
    def hexcode(cls, /):
        return cls.epitaph.hexcode

    @property
    def hashint(cls, /):
        return cls.epitaph.hashint

    @property
    def hashID(cls, /):
        return cls.epitaph.hashID

    ### Methods relating to serialising and unserialising classes:

    def get_class_epitaph(cls, /):
        raise NotImplementedError

    @property
    @_caching.soft_cache('_cls_softcache')
    def epitaph(cls, /):
        if '_epitaph' in cls.__dict__:
            return cls._epitaph
        return cls.get_class_epitaph()


class EssenceBase(metaclass=Essence):

    _ptolemaic_mergetuples__ = ('_ptolemaic_mroclasses__',)
    _ptolemaic_mergedicts__ = ()
    _ptolemaic_mroclasses__ = ()

    @classmethod
    def get_class_epitaph(cls, /):
        return cls.taphonomy.auto_epitaph(cls)

    @classmethod
    def __class_repr__(cls, /):
        return cls.__qualname__

    @classmethod
    def __class_str__(cls, /):
        return cls.__name__


###############################################################################
###############################################################################
