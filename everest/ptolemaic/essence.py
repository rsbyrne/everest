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
    reseed as _reseed,
    FrozenMap as _FrozenMap,
    )

from everest.ptolemaic.pleroma import Pleroma as _Pleroma


def ordered_set(itr):
    return tuple(_mitertools.unique_everseen(itr))

_mprox = _types.MappingProxyType


### Implementing mergetuples and mergedicts:

def yield_mergees(bases, namespace, name, /):
    for base in bases:
        if hasattr(base, name):
            yield getattr(base, name)
    if name in namespace:
        yield namespace[name]

def gather_names_tuplelike(bases, namespace, name, /):
    mergees = tuple(yield_mergees(bases, namespace, name))
    for i, mergee in enumerate(mergees):
        latter = set(_itertools.chain.from_iterable(mergees[i+1:]))
        yield from (val for val in mergee if not val in latter)

def gather_names_dictlike(bases, namespace, name, /):
    mergees = tuple(yield_mergees(bases, namespace, name))
    for i, mergee in enumerate(mergees):
        latter = set(_itertools.chain.from_iterable(mergees[i+1:]))
        for key in mergee:
            if not key in latter:
                yield key, mergee[key]

_GATHERMETHNAMES = {
    _FrozenMap: gather_names_dictlike,
    }

def merge_names(bases, namespace, name, /, *, mergetyp=tuple):
    meth = _GATHERMETHNAMES.get(mergetyp, gather_names_tuplelike)
    namespace[name] = mergetyp(meth(bases, namespace, name))

def merge_names_all(bases, namespace, overname, /, **kwargs):
    merge_names(bases, namespace, overname)
    for name in namespace[overname]:
        merge_names(bases, namespace, name, **kwargs)

def expand_bases(bases):
    '''Expands any pseudoclasses from the input list of bases.'''
    seen = set()
    for base in bases:
        if not isinstance(base, Essence):
            yield base
        elif getattr(base, '_ptolemaic_fuserclass_', False):
            for subbase in expand_bases(base.__bases__):
                if subbase not in seen:
                    yield subbase
                    seen.add(subbase)
        else:
            yield base._ptolemaic_class__


class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Implementing mroclasses:

    def _make_mroclass(cls, name: str, /):
        adjname = f'_mroclassbase_{name}__'
#         fusename = f'_mroclassfused_{name}__'
        if name in cls.__dict__:
            setattr(cls, adjname, cls.__dict__[name])
        inhclasses = []
        for mcls in cls.__mro__:
            searchname = adjname if isinstance(mcls, Essence) else name
            if searchname in mcls.__dict__:
                if not (inhcls := mcls.__dict__[searchname]) in inhclasses:
                    inhclasses.append(inhcls)
        inhclasses = tuple(inhclasses)
        if not inhclasses:
            return NotImplemented
        if len(inhclasses) == 1:
            return inhclasses[0]
        if all(issubclass(inhclasses[-1], inh) for inh in inhclasses[:-1]):
            return inhclasses[-1]
        return type(
            name,
            inhclasses,
            {'__slots__':(), '_ptolemaic_fuserclass_': True},
            )

    def _add_mroclass(cls, name: str, /):
        out = cls._make_mroclass(name)
        if out is not NotImplemented:
            setattr(cls, name, out)

    def _add_mroclasses(cls, /):
        for name in cls.MROCLASSES:
            cls._add_mroclass(name)

    ### Creating the object that is the class itself:

    @classmethod
    def __prepare__(meta, name, bases, /, *args, **kwargs):
        '''Called before class body evaluation as the namespace.'''
        return dict()

    @classmethod
    def __meta_init__(meta, /):
        pass

    @classmethod
    def process_mergenames(meta, bases, namespace):
        merge_names_all(bases, namespace, 'MERGETUPLES')
        merge_names_all(
            bases, namespace, 'MERGEDICTS',
            mergetyp=_FrozenMap,
            )
        merge_names_all(
            bases, namespace, 'MERGESETS',
            mergetyp=frozenset,
            )

    @classmethod
    def process_annotations(meta, namespace):
        namespace['__annotations__'] = _types.MappingProxyType(
            namespace.get('__annotations__', empty := {})
            | namespace.get('__extra_annotations__', empty)
            )

    @property
    def softcache(cls, /):
        try:
            return cls.__dict__['_clssoftcache']
        except KeyError:
            with cls.mutable:
                out = cls._clssoftcache = {}
            return out

    @property
    def weakcache(cls, /):
        try:
            return cls.__dict__['_clsweakcache']
        except KeyError:
            with cls.mutable:
                out = cls._clsweakcache = _weakref.WeakValueDictionary()
            return out

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):

        bases = list(expand_bases(bases))
        for basetyp in meta.basetypes:
            for base in bases:
                if basetyp in base.__mro__:
                    break
            else:
                bases.append(basetyp)
        bases = tuple(bases)

        if '__slots__' not in namespace:
            namespace['__slots__'] = ()
        meta.process_mergenames(bases, namespace)
        namespace['_clssoftcache'] = {}
        namespace['_clsweakcache'] = _weakref.WeakValueDictionary()
        meta.process_annotations(namespace)

        return name, bases, namespace

    @classmethod
    def get_meta(meta, bases):
        return meta

    @classmethod
    def __meta_call__(meta, /, *args, **kwargs):
        '''Called when the metaclass is called, '''
        ''' e.g. during class statement execution with metaclass=meta.'''
        out = meta.__class_construct__(*args, **kwargs)
        meta.__init__(out, *args, **kwargs)
        return out

    def __new__(meta, /, *args, **kwargs):
        '''Called when using the type constructor directly, '''
        '''e.g. type(name, bases, namespace) -'''
        '''__init__ is called implicitly.'''
        return meta.__class_construct__(*args, **kwargs)

    @classmethod
    def create_class_object(meta, name, bases, namespace):
        return _abc.ABCMeta.__new__(
            meta.get_meta(bases), name, bases, namespace
            )

    @classmethod
    def __class_construct__(meta,
            name: str = None,
            bases: tuple = (),
            namespace: dict = None,
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
        name, bases, namespace = \
            meta.pre_create_class(name, bases, namespace)
        return meta.create_class_object(name, bases, namespace)

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        cls.__class_pre_init__(*args, **kwargs)
        cls.__class_deep_init__()
        cls.__class_init__()
        cls.freezeattr.toggle(True)

    def __class_pre_init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(cls, *args, **kwargs)

    def __class_deep_init__(cls, /):
        cls._add_mroclasses()

    def __class_init__(cls, /):
        pass

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

    ### Aliases:

    @property
    def _ptolemaic_class__(cls, /):
        return cls

    def get_attributes(cls, /):
        lst = list()
        for ACls in cls.__mro__:
            preserve = ACls.__dict__.get('PRESERVEORDER', set())
            for name in ACls.__dict__:
                if name.startswith('__'):
                    continue
                if name in lst:
                    if name in preserve:
                        continue
                    else:
                        lst.remove(name)
                        lst.append(name)
                else:
                    lst.append(name)
        return tuple(lst)

    @property
    def attributes(cls, /):
        return cls.get_attributes()

    ### What happens when the class is called:

    @property
    def __call__(cls, /):
        return cls.__class_call__

    ### Methods relating to class serialisation:

    @property
    def metacls(cls, /):
        return type(cls._ptolemaic_class__)

    @property
    def taphonomy(cls, /):
        return cls.metacls.taphonomy

    def get_clsepitaph(cls, /):
        return cls.taphonomy.auto_epitaph(cls._ptolemaic_class__)

    @property
    @_caching.soft_cache()
    def epitaph(cls, /):
        return cls._ptolemaic_class__.get_clsepitaph()

    ### Representations:

    def __class_repr__(cls, /):
        return cls.__qualname__

    def __class_str__(cls, /):
        return cls.__name__

    @_caching.soft_cache()
    def __repr__(cls, /):
        return cls.__class_repr__()

    @_caching.soft_cache()
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

    @_caching.soft_cache()
    def __hash__(cls, /):
        return _reseed.rdigits(12)


class EssenceBase(metaclass=Essence):

    MERGETUPLES = ('MROCLASSES',)

    @classmethod
    def __class_init__(cls, /):
        pass


###############################################################################
###############################################################################
