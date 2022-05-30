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
    ARITHMOPS as _ARITHMOPS, REVOPS as _REVOPS,
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


class ClassBodyProcessor(dict):

    def __init__(self, meta, name, bases, /):
        self._preprocess = meta._process_namespace_entry
        bases = meta.process_bases(name, bases)
        self.name, self.bases = name, bases
        super().__init__()

    def __setitem__(self, name, val, /):
        super().__setitem__(*self._preprocess(self, name, val))

    def __repr__(self, /):
        return f"ClassBodyProcessor({super().__repr__()})"


@_Ptolemaic.register
class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

#     ### Descriptor stuff:

#     def __set_name__(cls, owner, name, /):
#         try:
#             meth = cls.__class_set_name__
#         except AttributeError:
#             pass
#         else:
#             meth(owner, name)

#     def __get__(cls, instance, owner=None, /):
#         try:
#             meth = cls.__class_get__
#         except AttributeError:
#             return cls
#         else:
#             return meth(instance, owner)

#     def __set__(cls, instance, value, /):
#         try:
#             meth = cls.__class_set__
#         except AttributeError as exc:
#             raise AttributeError from exc
#         else:
#             return cls.__class_set__(instance, value)

#     def __delete__(cls, instance, /):
#         try:
#             meth = cls.__class_delete__
#         except AttributeError as exc:
#             raise AttributeError from exc
#         else:
#             return meth(instance)

#     ### Arithmetic:

#     for methname in _itertools.chain(_ARITHMOPS, _REVOPS):
#         exec('\n'.join((
#             f"@property",
#             f"def {methname}(cls, /):",
#             f"    try:",
#             f"        return cls.__class_{methname.strip('_')}__",
#             f"    except AttributeError:",
#             f"        raise NotImplementedError",
#             )))
#     del methname

    ### Implementing mroclasses:

    def _gather_mrobases(cls, name: str, /):
        for base in cls.__bases__:
            try:
                candidate = getattr(base, name)
            except AttributeError:
                continue
            try:
                yield candidate.__mroclass__
            except AttributeError:
                yield candidate
            # if not isinstance(base, Essence):
            #     continue
            # # if name in base.MROCLASSES:
            # #     yield getattr(base, f"_mrofused_{name}")
            # elif hasattr(base, name):
            #     yield getattr(base, name).__mroclass__

    @property
    def __mroclass__(cls, /):
        return cls.__dict__.get('_mroclass', cls.__ptolemaic_class__)

    def _make_mroclass(cls, name: str, /):
        bases = tuple(cls._gather_mrobases(name))
        if not all(isinstance(base, Essence) for base in bases):
            raise TypeError("All mroclass bases must be Essences.", bases)
        if name in cls.__dict__:
            homebase = cls.__dict__[name].__mroclass__
            if not isinstance(homebase, Essence):
                raise TypeError(
                    "All mroclass bases must be Essences.", homebase
                    )
            mrobasename = f"<mrobase_{name}>"
            # setattr(cls, mrobasename, homebase)
            if is_innerclass(homebase, cls):
                with homebase.mutable:
                    homebase.__qualname__ = \
                        f"{cls.__qualname__}.{mrobasename}"
            bases = (homebase, *bases)
        if not bases:
            bases = (Essence.BaseTyp,)
            # return
        mrofusedname = f"<mrofused_{name}>"
        ns = {
            '_ptolemaic_contexts': (*cls.contexts, cls),
            '__module__': cls.__module__,
            '__qualname__': f"{cls.__qualname__}.{mrofusedname}",
            }
        fused = type(name, bases, ns)
        # setattr(cls, mrofusedname, fused)
        bases = (fused, *(
            getattr(cls, oname)
            for oname in fused.OVERCLASSES
            if hasattr(cls, oname)
            ))
        ns = {
            '_ptolemaic_owners': (*cls.contexts, cls),
            '__module__': cls.__module__,
            '__qualname__': f"{cls.__qualname__}.{name}",
            '_mroclass': fused,
            }
        final = type(name, bases, ns)
        setattr(cls, name, final)
        try:
            meth = final.__set_name__
        except AttributeError:
            pass
        else:
            meth(cls, name)
        return final

    def _add_mroclass(cls, name: str, /):
        setattr(cls, name, cls._make_mroclass(name))

    def _add_mroclasses(cls, /):
        for name in cls.MROCLASSES:
            cls._add_mroclass(name)

    @property
    def contexts(cls, _default=(), /):
        return cls.__ptolemaic_class__.__dict__.get(
            '_ptolemaic_contexts', _default
            )

    @property
    def context(cls, /):
        try:
            return cls.contexts[-1]
        except IndexError:
            return None

    @property
    def truecontext(cls, /):
        try:
            return cls.contexts[0]
        except IndexError:
            return None

    ### Creating the object that is the class itself:

    @classmethod
    def process_bases(meta, name, bases, /):
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
    def __prepare__(*args, **kwargs):
        '''Called before class body evaluation as the namespace.'''
        return ClassBodyProcessor(*args)

    @classmethod
    def _process_namespace_entry(cls, processor, name, val, /):
        # print(name, val)
        return name, val

    @classmethod
    def __meta_init__(meta, /):
        pass

    @classmethod
    def process_mergename(meta, bases, ns, mergename, /):
        if isinstance(mergename, tuple):
            mergename, mergetyp = mergename
            mergetyp = _ur.convert_type(mergetyp)
        else:
            mergename, mergetyp = mergename, _ur.DatUniqueTuple
        ns[mergename] = merge_names(bases, ns, mergename, mergetyp=mergetyp)

    @classmethod
    def process_mergenames(meta, bases, ns, /):
        mergenames = ns['MERGENAMES'] = merge_names(
            bases, ns, 'MERGENAMES', mergetyp=_ur.DatUniqueTuple
            )
        for mergename in mergenames:
            meta.process_mergename(bases, ns, mergename)

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
        ns = dict(ns)
        if '__slots__' not in ns:
            ns['__slots__'] = ()
        ns['__annotations__'] = _ur.DatDict(meta.process_annotations(ns))
        meta._categorise_namespace(ns)
        meta.process_mergenames(bases, ns)
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
        out = meta.__class_construct__(*args)
        meta.__init__(out, *args, **kwargs)
        return out

    def __new__(meta, /, *args):
        '''Called when using the type constructor directly, '''
        '''e.g. type(name, bases, namespace); '''
        '''__init__ is called implicitly.'''
        return meta.__class_construct__(*args)

    @classmethod
    def __class_construct__(meta, name: str, bases: tuple, ns: dict, /):
        if isinstance(ns, ClassBodyProcessor):
            processor = ns
        else:
            processor = ClassBodyProcessor(meta, name, bases)
            processor.update(ns)
        bases = processor.bases
        ns = dict(processor)
        return _abc.ABCMeta.__new__(
            meta, *meta.pre_create_class(name, bases, ns)
            )

    ### Initialising the class:

    def __init__(cls, name, bases, ns, /):
        _abc.ABCMeta.__init__(cls, name, bases, ns)
        cls.__class_deep_init__()
        cls.freezeattr.toggle(True)

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

    @property
    def epitaph(cls, /):
        try:
            return cls.__dict__['_epitaph']
        except KeyError:
            epi = cls.taphonomy.auto_epitaph(cls)
            with cls.mutable:
                setattr(cls, '_epitaph', epi)
            return epi

    ### Operations:

    def __bool__(cls, /):
        return True

    ### Representations:

    def __class_repr__(cls, /):
        return f"{type(cls).__name__}:{cls.__qualname__}"

    def __class_str__(cls, /):
        return cls.__name__

    def __repr__(cls, /):
        return cls.__ptolemaic_class__.__class_repr__()

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
    def _get_signature(cls, /):
        try:
            func = cls.__class_call__
        except AttributeError:
            func = lambda: None
        return _inspect.signature(func)

    @classmethod
    def __class_deep_init__(cls, /):
        try:
            func = cls.__dict__['__class_delayed_eval__']
        except KeyError:
            pass
        else:
            func(ns := _RestrictedNamespace(badvals={cls,}))
            cls.incorporate_namespace(ns)
        cls._add_mroclasses()
        cls.__class_init__()
        cls.__signature__ = cls._get_signature()

    @classmethod
    def __class_init__(cls, /):
        pass


###############################################################################
###############################################################################
