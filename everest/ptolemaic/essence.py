###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import more_itertools as _mitertools
import weakref as _weakref
import operator as _operator
import types as _types
import collections as _collections

from everest.utilities import (
    caching as _caching,
    switch as _switch,
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
        out.freezeattr.toggle(True)
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
    def freezeattr(cls, /):
        try:
            return cls.__dict__['_clsfreezeattr']
        except KeyError:
            super().__setattr__(
                '_clsfreezeattr', switch := _switch.Switch(False)
                )
            return switch

    @property
    def mutable(cls, /):
        return cls.freezeattr.as_(False)

    def __setattr__(cls, key, val, /):
        if cls.freezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(cls)} "
                "is forbidden at this time; "
                f"toggle switch `.freezeattr` to override."
                )
        super().__setattr__(key, val)

    ### Implementing mergetuples and mergedicts:

    def _yield_mergees(cls, name, /):
        for base in cls.__bases__:
            if hasattr(base, name):
                yield getattr(base, name)
        if name in (dct := cls.__dict__):
            yield dct[name]

    def _gather_names_tuplelike(cls, name, /):
        mergees = tuple(cls._yield_mergees(name))
        for i, mergee in enumerate(mergees):
            latter = set(_itertools.chain.from_iterable(mergees[i+1:]))
            yield from (val for val in mergee if not val in latter)

    def _gather_names_dictlike(cls, name, /):
        mergees = tuple(cls._yield_mergees(name))
        for i, mergee in enumerate(mergees):
            latter = set(_itertools.chain.from_iterable(mergees[i+1:]))
            for key in mergee:
                if not key in latter:
                    yield key, mergee[key]

    _gathernamemeths = {
        tuple: _gather_names_tuplelike,
        _types.MappingProxyType: _gather_names_dictlike,
        }

    def _merge_names(cls, name, /, *, mergetyp=tuple):
        merged = mergetyp(cls._gathernamemeths[mergetyp](cls, name))
        setattr(cls, name, merged)

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

    def _process_mergers(cls, /):
        cls._merge_names('MERGETUPLES')
        cls._merge_names('MERGEDICTS')
        cls._merge_names_all('MERGETUPLES')
        cls._merge_names_all('MERGEDICTS', mergetyp=_types.MappingProxyType)

    def _process_mroclasses(cls, /):
        for name in cls.MROCLASSES:
            cls._add_mroclass(name)

    ### Handling annotations:

    def _process_annotations(cls, /):
        clsdct = cls.__dict__
        if (annokey := '__annotations__') in clsdct:
            anno = clsdct[annokey]
        else:
            setattr(cls, annokey, anno := {})
        if (extkey := '_extra_annotations__') in clsdct:
            anno.update(clsdct[extkey])
        setattr(cls, annokey, _types.MappingProxyType(anno))            

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(type(cls), cls, *args, **kwargs)
        cls._process_annotations()
        cls._process_mergers()
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

    def __class_contains__(cls, arg, /):
        return super().__contains__(arg)

    def __contains__(cls, arg, /):
        return cls._ptolemaic_class__.__class_contains__(arg)

    ### Methods relating to class serialisation:

    @property
    def metacls(cls, /):
        return type(cls._ptolemaic_class__)

    @property
    def taphonomy(cls, /):
        return cls.metacls.metataphonomy

    def get_clsepitaph(cls, /):
        return cls.taphonomy.auto_epitaph(cls._ptolemaic_class__)

    @property
    @_caching.soft_cache('_cls_softcache')
    def epitaph(cls, /):
        ptolcls = cls._ptolemaic_class__
        if '_clsepitaph' in (dct := ptolcls.__dict__):
            return dct['_clsepitaph']
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
    def hexcode(cls, /):
        return cls.epitaph.hexcode

    @property
    def hashint(cls, /):
        return cls.epitaph.hashint

    @property
    def hashID(cls, /):
        return cls.epitaph.hashID

    def __hash__(cls, /):
        return cls.hashint

    ### Handy methods:

    def _yield_attributes(cls, /):
        seen = set()
        for ACls in cls.__mro__:
            for name in ACls.__dict__:
                if name.startswith('__'):
                    continue
                if name in seen:
                    continue
                yield name
                seen.add(name)

    @property
    def attributes(cls, /):
        return tuple(reversed(tuple(cls._yield_attributes())))


class EssenceBase(metaclass=Essence):

    MERGETUPLES = ('MROCLASSES',)
    MERGEDICTS = ()
    MROCLASSES = ()

    @classmethod
    def __class_init__(cls, /):
        pass


###############################################################################
###############################################################################
