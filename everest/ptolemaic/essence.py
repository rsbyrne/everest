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

gathernamemeths = {
    tuple: gather_names_tuplelike,
    _types.MappingProxyType: gather_names_dictlike,
    }

def merge_names(bases, namespace, name, /, *, mergetyp=tuple):
    meth = gathernamemeths[mergetyp]
    namespace[name] = mergetyp(meth(bases, namespace, name))

def merge_names_all(bases, namespace, overname, /, **kwargs):
    merge_names(bases, namespace, overname)
    for name in namespace[overname]:
        merge_names(bases, namespace, name, **kwargs)


class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

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
            mergetyp=_types.MappingProxyType
            )

    @classmethod
    def process_annotations(meta, namespace):
        namespace['__annotations__'] = _types.MappingProxyType(
#             meta.BaseTyp.__dict__.get('__annotations__', (empty := {}))
            namespace.get('__annotations__', empty := {})
            | namespace.get('__extra_annotations__', empty)
            )

    @property
    def softcache(cls, /):
        try:
            return cls._ptolemaic_class__.__dict__['_clssoftcache']
        except KeyError:
            with (ptolcls := cls._ptolemaic_class__).mutable:
                out = ptolcls._clssoftcache = {}
            return out

    @property
    def weakcache(cls, /):
        try:
            return cls._ptolemaic_class__.__dict__['_clsweakcache']
        except KeyError:
            with (ptolcls := cls._ptolemaic_class__).mutable:
                out = ptolcls._clsweakcache = _weakref.WeakValueDictionary()
            return out

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):

        bases = [*bases]
        for basetyp in meta.basetypes:
            for base in bases:
                if issubclass(base, basetyp):
                    break
            else:
                if basetyp not in bases:
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
    def __class_construct__(meta,
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
        name, bases, namespace = meta.pre_create_class(name, bases, namespace)
        out = _abc.ABCMeta.__new__(meta, name, bases, namespace)
        meta.__init__(out, *args, **kwargs)
        out.__class_init__()
        out.freezeattr.toggle(True)
        return out

    ### Implementing the attribute-freezing behaviour for classes:

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

    def _process_mroclasses(cls, /):
        for name in cls.MROCLASSES:
            cls._add_mroclass(name)

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(type(cls), cls, *args, **kwargs)
        if hasattr(cls, 'MROCLASSES'):
            cls._process_mroclasses()

    def __class_init__(cls, /):
        pass

    ### Aliases:

    @property
    def _ptolemaic_class__(cls, /):
        return cls

    ### What happens when the class is called:

    @property
    def __call__(cls, /):
        return cls.__class_call__

    ### Methods relating to class inheritance and getitem behaviour:

#     def __class_contains__(cls, arg, /):
#         return super().__contains__(arg)

#     @property
#     def __contains__(cls, /):
#         return cls._ptolemaic_class__.__class_contains__

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

#     @_caching.soft_cache('_clssoftcache')
    def __repr__(cls, /):
        return cls.__class_repr__()

#     @_caching.soft_cache('_clssoftcache')
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
#         return cls.hashint


class EssenceBase(metaclass=Essence):

    @classmethod
    def __class_init__(cls, /):
        pass


###############################################################################
###############################################################################
