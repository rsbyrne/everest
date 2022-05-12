###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import more_itertools as _mitertools
import weakref as _weakref
import types as _types
import inspect as _inspect
import functools as _functools

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    FrozenMap as _FrozenMap,
    RestrictedNamespace as _RestrictedNamespace,
    misc as _misc,
    )
from everest import bureau as _bureau
from everest.ur import Dat as _Dat

from .ptolemaic import Ptolemaic as _Ptolemaic
from .pleroma import Pleroma as _Pleroma
from . import exceptions as _exceptions


class MROClassNotFound(
        _exceptions.PtolemaicLayoutException,
        _exceptions.PtolemaicExceptionRaisedBy,
        AttributeError,
        ):

    def __init__(self, /, mroname, *args, **kwargs):
        self.mroname = mroname
        super().__init__(*args, **kwargs)

    def message(self, /):
        yield from super().message()
        yield f"when no bases could be found for mro name {self.mroname}"


class MROSubClassRecursion(
        _exceptions.PtolemaicLayoutException,
        _exceptions.PtolemaicExceptionRaisedBy,
        TypeError,
        ):

    def __init__(self, /, mroname, *args, **kwargs):
        self.mroname = mroname
        super().__init__(*args, **kwargs)

    def message(self, /):
        yield from super().message()
        yield f"when attempting to recursively subclass {self.mroname}"


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
@_Dat.register
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
                    homebase.__qualname__ = f"{cls.__qualname__}.{mrobasename}"
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
    def process_mergenames(meta, name, bases, namespace, /):
        bases = (meta, *bases)
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
    def process_annotations(meta, name, bases, namespace, /):
        namespace['__annotations__'] = _types.MappingProxyType(
            namespace.get('__annotations__', empty := {})
            | namespace.get('__extra_annotations__', empty)
            )

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
#         out = []
#         for base in bases:
#             if base not in out:
#                 out.append(bases)
#         return tuple(out)

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):
        bases = meta.process_bases(name, bases, namespace)
        if '__slots__' not in namespace:
            namespace['__slots__'] = ()
        meta.process_mergenames(name, bases, namespace)
        for key, val in tuple(namespace['ADJNAMES'].items()):
            try:
                namespace[val] = namespace[key]
            except KeyError:
                pass
            else:
                del namespace[key]
        namespace['_clssoftcache'] = {}
        namespace['_clsweakcache'] = _weakref.WeakValueDictionary()
        namespace['__weak_dict__'] = _weakref.WeakValueDictionary()
        meta.process_annotations(name, bases, namespace)
        return name, bases, namespace

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
    def create_class_object(meta, name, bases, namespace):
        meta = meta.get_meta(bases)
        return _abc.ABCMeta.__new__(meta, name, bases, namespace)

    @classmethod
    def __class_construct__(meta,
            name: str, bases: tuple, namespace: dict, /
            ):
        return meta.create_class_object(*meta.pre_create_class(
            name, bases, namespace
            ))

    ### Storage:

    @property
    def softcache(cls, /):
        return cls._clssoftcache

    @property
    def weakcache(cls, /):
        return cls._clsweakcache

    @property
    @_caching.weak_cache()
    def tab(cls, /):
        return _bureau.request_tab(cls)

    @property
    @_caching.weak_cache()
    def tray(cls, /):
        return _bureau.request_tray(cls)

    @property
    @_caching.weak_cache()
    def drawer(cls, /):
        return _bureau.request_drawer(cls)

    @property
    def taphonomy(cls, /):
        try:
            return cls.tab._taphonomy
        except AttributeError:
            out = cls.tab._taphonomy = _bureau.get_current_bureau().taphonomy
            return out

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
            # if (owners := cls.owners):
            #     cls.__qualname__ = '.'.join(
            #         ACls.__qualname__ for ACls in (cls.owner, cls)
            #         )
            cls.__class_init__()


    def incorporate_namespace(cls, ns, /):
        for key, val in ns.items():
            setattr(cls, key, val)

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

    @property
    def __signature__(cls, /):
        return cls.sig

    @property
    @_caching.soft_cache()
    def sig(cls, /):
        return cls._get_sig()

    ### Methods relating to class serialisation:

    @property
    def metacls(cls, /):
        return type(cls.__ptolemaic_class__)

    @property
    @_caching.soft_cache()
    def epitaph(cls, /):
        return cls.taphonomy.auto_epitaph(cls.__ptolemaic_class__)

    ### Operations:

    def __bool__(cls, /):
        return True

    ### Representations:

    # @property
    # @_caching.soft_cache()
    # def __qualname__(cls, /):
    #     return '.'.join((*cls.owners, cls.__name__))

    def __class_repr__(cls, /):
        return f"{type(cls).__name__}:{cls.__qualname__}"

    def __class_str__(cls, /):
        return cls.__name__

    @_caching.soft_cache()
    def __repr__(cls, /):
        return cls.__class_repr__()

    @_caching.soft_cache()
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

    def __hash__(cls, /):
        return id(cls)


class EssenceBase(_Ptolemaic, metaclass=Essence):

    MERGETUPLES = ('MROCLASSES', 'OVERCLASSES')
    MERGEDICTS = ('ADJNAMES',)

    @classmethod
    def __class_call__(cls, /, *_, **__):
        raise NotImplementedError

    @classmethod
    def _get_sig(cls, /):
        return _inspect.signature(cls.__class_call__)

    @classmethod
    def __class_init__(cls, /):
        cls._add_mroclasses()


###############################################################################
###############################################################################
