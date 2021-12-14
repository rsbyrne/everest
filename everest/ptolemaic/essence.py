###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import more_itertools as _mitertools
import weakref as _weakref
import operator as _operator

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    FrozenMap as _FrozenMap,
    )

from everest.ptolemaic.pleroma import Pleroma as _Pleroma


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))


class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Creating the object that is the class itself:

    @classmethod
    def __prepare__(meta, name, bases, /, *args, **kwargs):
        return dict()

    @classmethod
    def _pleroma_init__(meta, /):
        pass

    @classmethod
    def process_bases(meta, bases):
        '''Inserts the metaclass's mandatory basetype if necessary.'''
        basetyp = meta.BaseTyp
        if not isinstance(bases, tuple):
            raise TypeError("Bad bases passed into class construct.")
        if tuple(filter(basetyp.__subclasscheck__, bases)):
            return bases
        return (*bases, basetyp)

    @classmethod
    def _create_class(meta, name, bases, namespace, /, *args, **kwargs):
        if '__slots__' not in namespace:
            namespace = {**namespace, '__slots__':()}
        out = meta.__new__(meta, name, bases, namespace)
        out._cls_softcache = {}
        out._cls_weakcache = _weakref.WeakValueDictionary()
        meta.__init__(out, *args, **kwargs)
        out.__class_init__()
        out.clsfreezeattr = True
        return out

    @classmethod
    def _pleroma_construct(meta,
            name: str = None,
            bases: tuple = (),
            namespace: dict = None,
            *args, **kwargs,
            ):
        if namespace is None:
            namespace = {}
        if name is None:
            name = ''.join(base.__name__ for base in bases)
            if not name:
                raise ValueError(
                    "Must provide at least one "
                    "of either a class name or a tuple of bases."
                    )
        bases = meta.process_bases(bases)
        return meta._create_class(name, bases, namespace, *args, **kwargs)

    ### Implementing the attribute-freezing behaviour for classes:

    @property
    def clsfreezeattr(cls, /):
        try:
            return cls.__dict__['_clsfreezeattr']
        except KeyError:
            super().__setattr__(
                '_clsfreezeattr', switch := _switch.Switch(False)
                )
            return switch

    @clsfreezeattr.setter
    def clsfreezeattr(cls, val, /):
        cls._clsfreezeattr.toggle(val)

    @property
    def clsmutable(cls, /):
        return cls.clsfreezeattr.as_(False)

    def __setattr__(cls, key, val, /):
        if cls.clsfreezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(cls)} "
                "is forbidden at this time; "
                f"toggle switch `.freezeattr` to override."
                )
        super().__setattr__(key, val)

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

    def _process_mroclasses(cls, /):
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

    ### Handling annotations:

    def _process_annotations(cls, /):
        clsdct = cls.__dict__
        if (annokey := '__annotations__') in clsdct:
            anno = clsdct[annokey]
        else:
            setattr(cls, annokey, anno := {})
        if (extkey := '_extra_annotations__') in clsdct:
            anno.update(clsdct[extkey])
        setattr(cls, annokey, _FrozenMap(anno))

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(type(cls), cls, *args, **kwargs)
        cls._process_annotations()
        cls._process_mroclasses()

    def __class_init__(cls, /):
        pass

    ### Aliases:

    @property
    def _ptolemaic_class__(cls, /):
        return cls

    ### What happens when the class is called:

    def __class_call__(cls, /, *_, **__):
        raise NotImplementedError

    @property
    def __call__(cls, /):
        return cls._ptolemaic_class__.__class_call__

    ### Methods relating to class inheritance and getitem behaviour:

#     def _ptolemaic_issubclass__(cls, arg, /):
#         return _abc.ABCMeta.__subclasscheck__(cls, arg)

#     def __subclasscheck__(cls, arg, /):
#         return cls._ptolemaic_class__._ptolemaic_issubclass__(arg)

#     def _ptolemaic_isinstance__(cls, arg, /):
#         return _abc.ABCMeta.__instancecheck__(cls, arg)

#     def __instancecheck__(cls, arg, /):
#         return cls._ptolemaic_class__._ptolemaic_isinstance__(arg)

    def _ptolemaic_getitem__(cls, arg, /):
        return super().__getitem__(arg)

    def __getitem__(cls, arg, /):
        return cls._ptolemaic_class__._ptolemaic_getitem__(arg)

    def _ptolemaic_contains__(cls, arg, /):
        return super().__contains__(arg)

    def __contains__(cls, arg, /):
        return cls._ptolemaic_class__._ptolemaic_contains__(arg)

    ### Methods relating to class serialisation:

    @property
    def metacls(cls, /):
        return type(cls._ptolemaic_class__)

    @property
    def clstaphonomy(cls, /):
        return cls._ptolemaic_class__.metacls.metataphonomy

    def get_clsepitaph(cls, /):
        return cls._ptolemaic_class__.clstaphonomy.auto_epitaph(cls)

    @property
    @_caching.soft_cache('_cls_softcache')
    def clsepitaph(cls, /):
        ptolcls = cls._ptolemaic_class__
        if '_clsepitaph' in ptolcls.__dict__:
            return ptolcls._clsepitaph
        return ptolcls.get_clsepitaph()

    ### Representations:

    def __class_repr__(cls, /):
        return cls.__qualname__

    def __class_str__(cls, /):
        return cls.__name__

    @_caching.soft_cache('_cls_softcache')
    def __repr__(cls, /):
        return cls.__class_repr__()

    @_caching.soft_cache('_cls_softcache')
    def __str__(cls, /):
        return cls._ptolemaic_class__.__class_str__()

    @property
    def clshexcode(cls, /):
        return cls.clsepitaph.hexcode

    @property
    def clshashint(cls, /):
        return cls.clsepitaph.hashint

    @property
    def clshashID(cls, /):
        return cls.clsepitaph.hashID

    def __hash__(cls, /):
        return cls.clshashint

    ### Handy methods:

    @property
    def attributes(cls, /):
        seen = set()
        for ACls in reversed(cls.__mro__):
            for name in ACls.__dict__:
                if name.startswith('__'):
                    continue
                if name in seen:
                    continue
                yield name
                seen.add(name)


class EssenceBase(metaclass=Essence):

    _ptolemaic_mergetuples__ = ('_ptolemaic_mroclasses__',)
    _ptolemaic_mergedicts__ = ()
    _ptolemaic_mroclasses__ = ()

    @classmethod
    def __class_init__(cls, /):
        pass


###############################################################################
###############################################################################
