###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
import more_itertools as _mitertools
import weakref as _weakref
import types as _types
import inspect as _inspect

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    reseed as _reseed,
    FrozenMap as _FrozenMap,
    RestrictedNamespace as _RestrictedNamespace,
    misc as _misc,
    )
from everest.ur import Dat as _Dat

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
            base = base._ptolemaic_class__
        if base not in seen:
            seen.add(base)
            yield base


class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Implementing mroclasses:

    def _process_mrobase(cls, inh, /):
        if isinstance(inh, str):
            if inh.startswith('.'):
                attrnames = iter(inh.strip('.').split('.'))
                inh = cls
                for attrname in attrnames:
                    inh = getattr(inh, attrname)
            else:
                inh = eval(inh)
        if isinstance(inh, type):
            inh = inh.__dict__.get('__mroclass_basis__', inh)
        else:
            try:
                inh = getattr(inh, '__mroclass_basis__')
            except AttributeError:
                raise TypeError
        if not isinstance(inh, Essence):
            raise TypeError
        return inh

    def _make_mroclass(cls, name: str, /, mixin=None):
        candidates = []
        try:
            inh = cls.__dict__[name]
        except KeyError:
            pass
        else:
            candidates.append(cls._process_mrobase(inh))
        for base in cls.__bases__:
            if not isinstance(base, Essence):
                continue
            try:
                inh = getattr(base, name)
            except AttributeError:
                continue
            candidates.append(inh)
        inhclasses = []
        for inh in candidates:
            inh = cls._process_mrobase(inh)
            if inh not in inhclasses:
                inhclasses.append(inh)
        if not inhclasses:
            raise MROClassNotFound(name, cls)
        if len(inhclasses) == 1:
            basis = inhclasses[0]
        else:
            basis = type(
                f"{name}_FusedUnder_{cls.__name__}",
                tuple(inhclasses),
                {},
                )
        ns = dict(
            __mroclass_basis__=basis,
            )
        typname = name
        if mixin is None:
            # typname = f"{cls.__name__}_{name}"
            bases = (basis,)
            owners = (*cls.owners, cls)
        else:
            if mixin is cls:
                owners = cls.owners
                ns['_ptolemaic_overclass'] = cls
            else:
                owners = (*cls.owners, cls)
            # typname = f"{cls.__name__}_{name}"
            bases = (basis, mixin)
            ns['__mroclass_mixin__'] = mixin
        ns['_ptolemaic_owners'] = owners
        out = type(typname, bases, ns)
        return out

    def _add_mroclass(cls, arg: (str, type), /, mixin=None):
        if not isinstance(arg, str):
            if not isinstance(arg, type):
                raise TypeError(arg)
            setattr(cls, arg.__name__, arg)
        name = arg
        try:
            out = cls._make_mroclass(name, mixin=mixin)
        except TypeError as exc:
            raise TypeError(cls, name, mixin) from exc
        setattr(cls, name, out)
        if hasattr(out, '__set_name__'):
            out.__set_name__(cls, name)
        return out

    def _try_add_mroclass(cls, arg: (str, type), /, mixin=None):
        try:
            cls._add_mroclass(arg, mixin=mixin)
        except MROClassNotFound:
            pass

    def _add_mroclasses(cls, /):
        for name in cls.MROCLASSES:
            cls._try_add_mroclass(name)

    def _add_subclass(cls, arg: str, /):
        if not arg in cls.SUBCLASSES:
            raise TypeError(
                "Cannot add subclass "
                "without declaring its name in .SUBCLASSES."
                )
        try:
            overclass = cls.__dict__['__mroclass_mixin__']
        except KeyError:
            pass
        else:
            if arg in overclass.SUBCLASSES:
                raise MROSubClassRecursion(arg, cls)
        return cls._add_mroclass(arg, mixin=cls)
        # try:
        #     set() = cls.__dict__['_subclasses']
        # except KeyError:
        #     dct = cls._subclasses = {}
        # dct[arg] = out
        # return out

    # @property
    # @_caching.soft_cache()
    # def subclasses(cls, /):
    #     try:
    #         dct = cls.__dict__['_subclasses']
    #     except KeyError:
    #         dct = cls._subclasses = {}
    #     return _types.MappingProxyType(dct)

    @property
    def __mroclass_basis__(cls, /):
        return cls.__dict__.get('__mroclass_basis__', cls)

    def _try_add_subclass(cls, arg: str, /):
        try:
            cls._add_subclass(arg)
        except (MROSubClassRecursion, MROClassNotFound):
            pass

    def _add_subclasses(cls, /):
        for name in cls.SUBCLASSES:
            cls._try_add_subclass(name)

    @property
    def owners(cls, _default=(), /):
        return cls._ptolemaic_class__.__dict__.get('_ptolemaic_owners', _default)

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

    @property
    def overclass(cls, /):
        return cls.__dict__.get('_ptolemaic_overclass', None)

    ### Creating the object that is the class itself:

    @classmethod
    def __prepare__(meta, name, bases, /, *args, **kwargs):
        '''Called before class body evaluation as the namespace.'''
        return dict()

    @classmethod
    def __meta_init__(meta, /):
        pass

#     MERGETUPLES = ('MROCLASSES',)

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
        return _abc.ABCMeta.__new__(
            meta.get_meta(bases), name, bases, namespace
            )

    @classmethod
    def __class_construct__(meta,
            name: str, bases: tuple, namespace: dict, /
            ):
        return meta.create_class_object(*meta.pre_create_class(
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
            if (ocls := cls.overclass):
                cls.__qualname__ = '.'.join(
                    (ocls.__qualname__, cls.__name__)
                    )
            elif (owners := cls.owners):
                cls.__qualname__ = '.'.join(
                    ACls.__qualname__ for ACls in (cls.owner, cls)
                    )
            if (owners := cls.owners):
                cls.__mroclass_init__()
            else:
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
    def _ptolemaic_class__(cls, /):
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
        return type(cls._ptolemaic_class__)

    @property
    def taphonomy(cls, /):
        return cls.metacls.taphonomy

    def get_clsepitaph(cls, /):
        try:
            return cls.__dict__['_clsepitaph']
        except KeyError:
            return cls.taphonomy.auto_epitaph(cls._ptolemaic_class__)

    @property
    @_caching.soft_cache()
    def epitaph(cls, /):
        return cls._ptolemaic_class__.get_clsepitaph()

    ### Operations:

    for methname in (*_misc.ARITHMOPS, *_misc.REVOPS):
        exec('\n'.join((
            f"def __{methname}__(cls, /, *args, **kwargs):",
            f"    try:",
            f"        meth = cls.__class_{methname}__",
            f"    except AttributeError:",
            f"        return NotImplemented",
            f"    return meth(*args, **kwargs)",
            )))
    for methname in ('__contains__', '__len__', '__iter__'):
        exec('\n'.join((
            f"def __{methname}__(cls, /, *args, **kwargs):",
            f"    return cls.__class_{methname}__(*args, **kwargs)",
            )))
    del methname

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
        return cls._ptolemaic_class__.__class_str__()

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

    @_caching.soft_cache()
    def __hash__(cls, /):
        return _reseed.rdigits(12)


_Dat.register(Essence)


class EssenceBase(metaclass=Essence):

    MERGETUPLES = ('MROCLASSES', 'SUBCLASSES')
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
        cls._add_subclasses()

    @classmethod
    def __mroclass_init__(cls, /):
        cls.__class_init__()


###############################################################################
###############################################################################
