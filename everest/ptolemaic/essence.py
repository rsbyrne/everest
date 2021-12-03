###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools
import itertools as _itertools
import more_itertools as _mitertools
import inspect as _inspect
import operator as _operator
import pickle as _pickle
# import typing as _typing
from collections import abc as _collabc

from everest import utilities as _utilities
from everest.utilities import (
    caching as _caching,
    FrozenMap as _FrozenMap,
    switch as _switch,
    classtools as _classtools
    )
from everest import chora as _chora

from everest.ptolemaic.pleroma import Pleroma as _Pleroma


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


def pass_fn(arg, /):
    return arg


class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Methods relating to the metaclass itself:

    @classmethod
    def _pleroma_init__(meta, /):
        pass

    @classmethod
    def _pleroma_construct(meta, /, *args, **kwargs):
        '''Call the metaclass to create a new class.'''
        return super(type(meta), meta).__call__(*args, **kwargs)

    ### Methods relating to the Incision Protocol for classes:

    def __instancecheck__(cls, arg, /):
        return cls._ptolemaic_isinstance__(arg)

    def __contains__(cls, arg, /):
        return arg in cls.clschora

    def __getitem__(cls, arg, /):
        return cls._chora_getitem__(arg)

    def class_retrieve(cls, arg, /):
        raise NotImplementedError("Retrieval not supported on this class.")

    def class_incise(cls, arg, /):
        raise NotImplementedError("Incision not supported on this class.")

    def class_trivial(cls, arg, /):
        return cls

    def _class_defer_chora_methods(cls, /):

        chcls = cls.ClassChora
        prefixes = chcls.PREFIXES
        defkws = chcls._get_defkws((f"cls.class_{st}" for st in prefixes))

        for prefix in prefixes:
            methname = f"class_{prefix}"
            if not hasattr(cls, methname):
                setattr(cls, methname, cls._class_chora_passthrough)

        exec('\n'.join((
            f"@classmethod",
            f"def _chora_getitem__(cls, arg, /):"
            f"    return cls.classchora.__getitem__(arg, {defkws})"
            )))
        cls._chora_getitem__ = eval('_chora_getitem__')

        for name in chcls.chorameths:
            new = f"class_{name}"
            exec('\n'.join((
                f"@classmethod",
                f"@_functools.wraps(chcls.{name})",
                f"def {new}(cls, /, *args):",
                f"    return cls.classchora.{name}(*args, {defkws})",
                )))
            setattr(cls, new, eval(new))

    ### Creating the object that is the class itself:

    @classmethod
    def __prepare__(meta, name, bases, /, *args, **kwargs):
        return dict()

    @classmethod
    def process_bases(meta, bases):
        '''Inserts the metaclass's mandatory basetype if necessary.'''
        basetyp = meta.BaseTyp
        if tuple(filter(basetyp.__subclasscheck__, bases)):
            return bases
        return (*bases, basetyp)

    def __new__(meta, name, bases, namespace, /, *args, **kwargs):
        bases = meta.process_bases(bases)
        namespace['__slots__'] = ()
        return super().__new__(meta, name, bases, namespace, *args, **kwargs)

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

    ### Implementing the 'freezeattr' behaviour:

    @property
    def classfreezeattr(cls, /):
        try:
            return cls.__dict__['_classfreezeattr']
        except KeyError:
            super().__setattr__(
                '_classfreezeattr', switch := _switch.Switch(False)
                )
            return switch

    @classfreezeattr.setter
    def classfreezeattr(cls, val, /):
        cls._classfreezeattr.toggle(val)

    @property
    def classmutable(cls, /):
        return cls.classfreezeattr.as_(False)

    def __setattr__(cls, key, val, /):
        if cls.classfreezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(cls)} "
                "is forbidden at this time; "
                f"toggle switch `.classfreezeattr` to override."
                )
        super().__setattr__(key, val)

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        with cls.classmutable:
            super().__init__(*args, **kwargs)
            cls._class_softcache = {}
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
                mergetyp=_utilities.FrozenMap,
                itermeth='items',
                )
            cls._add_mroclasses()
            try:
                cls.classchora = cls._get_classchora()
            except NotImplementedError:
                pass
            else:
                cls._class_defer_chora_methods()

    ### What happens when the class is called:

    def construct(cls, /):
        raise NotImplementedError

    @property
    def __call__(cls, /):
        return cls.construct

    ### Defining aliases and representations for classes:

    def __repr__(cls, /):
        return cls.__class_repr__()

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
    def hashcode(cls, /):
        return cls.epitaph.hashcode

    @property
    def hashint(cls, /):
        return cls.epitaph.hashint

    @property
    def hashID(cls, /):
        return cls.epitaph.hashID

    ### Methods relating to serialising and unserialising classes:

    @property
    @_caching.soft_cache('_class_softcache')
    def epitaph(cls, /):
        return cls.get_class_epitaph()


class EssenceBase(_classtools.ClassInit, metaclass=Essence):

    __slots__ = ()

    _ptolemaic_mergetuples__ = ('_ptolemaic_mroclasses__',)
    _ptolemaic_mergedicts__ = ()
    _ptolemaic_mroclasses__ = ()

    ClassChora = _chora.Sliceable

    @classmethod
    def __init_subclass__(cls, /, **kwargs):
        with cls.classmutable:
            super().__init_subclass__(**kwargs)

    ### Customisable methods relating to the Incision Protocol:

    @classmethod
    def _ptolemaic_isinstance__(cls, arg, /):
        '''Returns `False` as `Essence` types cannot be instantiated.'''
        return False

#         @classmethod
#         def _ptolemaic_issubclass__(cls, arg, /):
#             return _abc.ABCMeta.__subclasscheck__(cls, arg)

    @classmethod
    def _get_classchora(cls, /) -> 'Chora':
        return cls.ClassChora()

    ### Serialisation methods:

    @classmethod
    def get_class_epitaph(cls, /):
        return cls.taphonomy.auto_epitaph(cls)

    ### Legibility methods:

    @classmethod
    def __class_repr__(cls, /):
        return cls.__qualname__


###############################################################################
###############################################################################
