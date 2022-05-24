###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import weakref as _weakref
import types as _types
import inspect as _inspect
import functools as _functools
from collections import abc as _collabc

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    RestrictedNamespace as _RestrictedNamespace,
    )
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from .ptolemaic import Ptolemaic as _Ptolemaic
from .pleroma import Pleroma as _Pleroma


### Implementing mergetuples and mergedicts:

def yield_mergees(bases, namespace, name, /):
    for base in bases:
        if hasattr(base, name):
            yield getattr(base, name)
    if name in namespace:
        yield namespace[name]

def merge_names(bases, namespace, name, /, *, mergetyp):
    if issubclass(mergetyp, _collabc.Mapping):
        iterable = (_itertools.chain.from_iterable(
            mp.items() for mp in yield_mergees(bases, namespace, name)
            ))
    else:
        iterable = _itertools.chain.from_iterable(
        yield_mergees(bases, namespace, name)
        )
    return mergetyp(iterable)

def expand_bases(bases):
    '''Expands any pseudoclasses from the input list of bases.'''
    seen = set()
    for base in bases:
        if isinstance(base, Essence):
            base = base.__ptolemaic_class__
        if base not in seen:
            seen.add(base)
            yield base


def is_innerclass(inner, outer):
    if inner.__module__ is not outer.__module__:
        return False
    return '.'.join(inner.__qualname__.split('.')[:-1]) == outer.__qualname__


@_Ptolemaic.register
class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Implementing mroclasses:

    def _gather_mrobases(cls, name: str, /):
        for base in cls.__bases__:
            if not isinstance(base, Essence):
                continue
            if name in base.MROCLASSES:
                yield getattr(base, f"_mrofused_{name}")
            elif hasattr(base, name):
                candidate = getattr(base, name)
                if not isinstance(candidate, Essence):
                    continue
                yield candidate

    def _add_mroclass(cls, name: str, /):
        mrobases = tuple(cls._gather_mrobases(name))
        if not all(isinstance(base, Essence) for base in mrobases):
            raise TypeError("All mroclass bases must be Essences.", mrobases)
        if name in cls.__dict__:
            homebase = cls.__dict__[name]
            if not isinstance(homebase, Essence):
                raise TypeError(
                    "All mroclass bases must be Essences.", homebase
                    )
            mrobasename = f"_mrobase_{name}"
            setattr(cls, mrobasename, homebase)
            if is_innerclass(homebase, cls):
                with homebase.mutable:
                    homebase.__qualname__ = \
                        f"{cls.__qualname__}.{mrobasename}"
            mrobases = (homebase, *mrobases)
        if not mrobases:
            mrobases = (Essence.BaseTyp,)
            # return
        mrofusedname = f"_mrofused_{name}"
        ns = {
            '_ptolemaic_owners': (*cls.owners, cls),
            '__module__': cls.__module__,
            '__qualname__': f"{cls.__qualname__}.{mrofusedname}",
            }
        fused = type(name, mrobases, ns)
        setattr(cls, mrofusedname, fused)
        newbases = (fused, *(
            getattr(cls, oname)
            for oname in fused.OVERCLASSES
            if hasattr(cls, oname)
            ))
        ns = {
            '_ptolemaic_owners': (*cls.owners, cls),
            '__module__': cls.__module__,
            '__qualname__': f"{cls.__qualname__}.{name}",
            }
        final = type(name, newbases, ns)
        setattr(cls, name, final)

    def _add_mroclasses(cls, /):
        for name in cls.MROCLASSES:
            cls._add_mroclass(name)

    def _add_subclasses(cls, /):
        pass

    @property
    def owners(cls, _default=(), /):
        return cls.__ptolemaic_class__.__dict__.get(
            '_ptolemaic_owners', _default
            )

    @property
    def owner(cls, /):
        try:
            return cls.owners[-1]
        except IndexError:
            return None

    @property
    def trueowner(cls, /):
        try:
            return cls.owners[0]
        except IndexError:
            return None

    ### Creating the object that is the class itself:

    @classmethod
    def __prepare__(meta, name, bases, /, *args, **kwargs):
        '''Called before class body evaluation as the namespace.'''
        return dict()

    @classmethod
    def __meta_init__(meta, /):
        pass

    @classmethod
    def process_mergenames(meta, name, bases, ns, /):
        mergenames = ns['MERGENAMES'] = merge_names(
            bases, ns, 'MERGENAMES', mergetyp=_ur.DatUniqueTuple
            )
        for row in mergenames:
            if isinstance(row, tuple):
                name, mergetyp = row
                mergetyp = _ur.convert_type(mergetyp)
            else:
                name, mergetyp = row, _ur.DatUniqueTuple
            ns[name] = merge_names(bases, ns, name, mergetyp=mergetyp)

    @classmethod
    def process_bases(meta, name, bases, namespace, /):
        bases = list(expand_bases(bases))
        for basetyp in meta.basetypes:
            if basetyp is object:
                continue
            for base in bases:
                if basetyp in base.__mro__:
                    break
            else:
                bases.append(basetyp)
        return tuple(bases)

    @classmethod
    def process_annotations(meta, ns, /):
        return {
            key: (note, ns.pop(key, _inspect._empty))
            for key, note in ns.pop('__annotations__', {}).items()
            }

    @classmethod
    def _yield_namespace_categories(meta, ns, /):
        return
        yield

    @classmethod
    def _categorise_namespace(meta, ns, /):
        categories = tuple(meta._yield_namespace_categories(ns))
        for key, val in ns.items():
            for name, check, store in categories:
                if check(val):
                    store[key] = val
        ns.update(**{
            name: _types.MappingProxyType({**store})
            for name, check, store in categories
            })

    @classmethod
    def pre_create_class(meta, name, bases, ns, /):
        bases = meta.process_bases(name, bases, ns)
        if '__slots__' not in ns:
            ns['__slots__'] = ()
        ns['__annotations__'] = _types.MappingProxyType(
            meta.process_annotations(ns)
            )
        meta._categorise_namespace(ns)
        meta.process_mergenames(name, bases, ns)
        ns['_clssoftcache'] = {}
        ns['_clsweakcache'] = _weakref.WeakValueDictionary()
        ns['__weak_dict__'] = _weakref.WeakValueDictionary()
        ns['_clsfreezeattr'] = _switch.Switch(False)
        return name, bases, ns

    @classmethod
    def get_meta(meta, bases):
        return meta

    @classmethod
    def decorate(meta, obj, /):
        raise NotImplementedError(
            f"Metaclass {meta} cannot be used as a decorator"
            )

    @classmethod
    def __meta_call__(meta, arg0=None, /, *argn, **kwargs):
        if arg0 is None:
            if argn:
                raise ValueError("Must pass all args or none.")
            return _functools.partial(meta.decorate, **kwargs)
        elif not argn:
            return meta.decorate(arg0, **kwargs)
        args = (arg0, *argn)
        out = meta.__class_construct__(*args, **kwargs)
        meta.__init__(out, *args, **kwargs)
        return out

    def __new__(meta, /, *args, **kwargs):
        '''Called when using the type constructor directly, '''
        '''e.g. type(name, bases, namespace) -'''
        '''__init__ is called implicitly.'''
        return meta.__class_construct__(*args, **kwargs)

    @classmethod
    def __class_construct__(meta,
            name: str, bases: tuple, namespace: dict, /
            ):
        return _abc.ABCMeta.__new__(meta, *meta.pre_create_class(
            name, bases, namespace
            ))

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        with cls.mutable:
            _abc.ABCMeta.__init__(cls, *args, **kwargs)
            try:
                func = cls.__dict__['__class_delayed_eval__']
            except KeyError:
                pass
            else:
                func(ns := _RestrictedNamespace(badvals={cls,}))
                cls.incorporate_namespace(ns)
            cls.__class_init__()
            cls.__signature__ = cls._get_signature()


    def incorporate_namespace(cls, ns, /):
        for key, val in ns.items():
            setattr(cls, key, val)

    ### Storage:

    @property
    def softcache(cls, /):
        return cls._clssoftcache

    @property
    def weakcache(cls, /):
        return cls._clsweakcache

    @_caching.attr_property(weak=True, dictlook=True)
    def tray(cls, /):
        return _FOCUS.request_session_storer(cls)

    @_caching.attr_property(weak=True, dictlook=True)
    def drawer(cls, /):
        return _FOCUS.request_bureau_storer(cls)

    @property
    def taphonomy(cls, /):
        return _FOCUS.bureau.taphonomy

    ### Implementing the attribute-freezing behaviour for classes:

    @property
    def freezeattr(cls, /):
        return cls._clsfreezeattr

    @property
    def mutable(cls, /):
        return cls.freezeattr.as_(False)

    def __setattr__(cls, name, val, /):
        if cls.freezeattr:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )
        super().__setattr__(name, val)

    def __delattr__(cls, name, /):
        if cls.freezeattr:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )
        super().__delattr__(name)

    ### Aliases:

    @property
    def __ptolemaic_class__(cls, /):
        return cls

    def get_attributes(cls, /):
        lst = list()
        for ACls in reversed(cls.__mro__):
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

    def __class_instancecheck__(cls, obj, /):
        return issubclass(type(obj), cls)

    @property
    def __instancecheck__(cls, /):
        return cls.__class_instancecheck__

    ### What happens when the class is called:

    @property
    def __call__(cls, /):
        return cls.__class_call__

    ### Methods relating to class serialisation:

    @property
    def metacls(cls, /):
        return type(cls.__ptolemaic_class__)

    @_caching.attr_property(dictlook=True)
    def epitaph(cls, /):
        return cls.taphonomy.auto_epitaph(cls.__ptolemaic_class__)

    ### Operations:

    def __bool__(cls, /):
        return True

    ### Representations:

    def __class_repr__(cls, /):
        return f"{type(cls).__name__}:{cls.__qualname__}"

    def __class_str__(cls, /):
        return cls.__name__

    @_caching.attr_cache(dictlook=True)
    def __repr__(cls, /):
        return cls.__class_repr__()

    @_caching.attr_cache(dictlook=True)
    def __str__(cls, /):
        return cls.__ptolemaic_class__.__class_str__()

    def _repr_pretty_(cls, p, cycle, root=None):
        if root is not None:
            raise NotImplementedError
        p.text(cls.__qualname__)

    @property
    def hexcode(cls, /):
        return cls.epitaph.hexcode

    @property
    def hashint(cls, /):
        return cls.epitaph.hashint

    @property
    def hashID(cls, /):
        return cls.epitaph.hashID


class EssenceBase(_Ptolemaic, metaclass=Essence):

    MERGENAMES = ('MROCLASSES', 'OVERCLASSES')

    @classmethod
    def __class_call__(cls, /, *_, **__):
        raise NotImplementedError

    @classmethod
    def _get_signature(cls, /):
        return _inspect.signature(cls.__class_call__)

    @classmethod
    def __class_init__(cls, /):
        cls._add_mroclasses()


###############################################################################
###############################################################################
