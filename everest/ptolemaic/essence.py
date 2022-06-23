###############################################################################
''''''
###############################################################################


import abc as _abc
import functools as _functools

from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .pleroma import Pleroma as _Pleroma
from .classbody import ClassBody as _ClassBody
from .utilities import (
    BindableObject as _BindableObject,
    BoundObject as _BoundObject,
    )


@_ptolemaic.Ptolemaic.register
@_BindableObject.register
class Essence(_abc.ABCMeta, metaclass=_Pleroma):
    '''
    The metaclass of all Ptolemaic types;
    pure instances of itself are 'pure kinds' that cannot be instantiated.
    '''

    ### Descriptor stuff:

    def __set_name__(cls, owner, name, /):
        try:
            meth = cls.__class_set_name__
        except AttributeError:
            pass
        else:
            meth(owner, name)

    @property
    def __bound_get__(cls, /):
        return cls.__class_bound_get__

    @property
    def __bound_owner_get__(cls, /):
        return cls.__class_bound_owner_get__

    @property
    def __bound_set__(cls, /):
        return cls.__class_bound_set__

    @property
    def __bound_set__(cls, /):
        return cls.__class_bound_delete__

    @property
    def register_notion(cls, /):
        return cls._class_register_notion

    @property
    def register_organ(cls, /):
        return cls._class_register_organ

    @property
    def __corpus__(cls, /):
        try:
            return cls.__dict__['__class_corpus__']
        except KeyError:
            return None

    @property
    def __cosmic__(cls, /):
        return cls.__corpus__ is None

    @property
    def __relname__(cls, /):
        try:
            return cls.__dict__['__class_relname__']
        except KeyError:
            return cls.__qualname__


    ### Meta init:

    @classmethod
    def _yield_bodynametriggers(meta, /):
        return
        yield

    @classmethod
    def _yield_bodymeths(meta, /):
        return
        yield

    @classmethod
    def _yield_mergenames(meta, body, /):
        return
        yield

    @classmethod
    def __meta_init__(meta, /):
        pass

    ### Class construction:

    @classmethod
    def _pre_prepare_bases(meta, bases, /):
        bases = tuple(bases)
        yield from bases
        for metabase in (meta, *meta.__bases__):
            if isinstance(metabase, _Pleroma):
                try:
                    basetyp = metabase.BaseTyp
                except AttributeError:
                    continue
                if not any(issubclass(base, basetyp) for base in bases):
                    yield basetyp

    @classmethod
    def __prepare__(meta, name, bases, /, **kwargs):
        '''Called before class body evaluation as the namespace.'''
        return _ClassBody(
            meta, name, tuple(meta._pre_prepare_bases(bases)),
            _staticmeta_=(name == meta.basetypname), **kwargs,
            )

    @classmethod
    def body_handle_anno(meta, body, name, hint, val, /):
        raise TypeError(f"Annotations not supported for {meta}.")

    @classmethod
    def process_shadow(meta, body, name, val, /):
        raise TypeError(f"Shadow magic not supported for {meta}.")

    @classmethod
    def handle_slots(meta, body, slots, /):
        raise TypeError("Slots not supported under this metaclass.")
        # print(slots)
        # dict.__setitem__(body, '__slots__', slots)

    @classmethod
    def classbody_finalise(meta, body, /):
        pass

    @classmethod
    def decorate(meta, obj, /):
        raise NotImplementedError(
            f"Metaclass {meta} cannot be used as a decorator"
            )

    @classmethod
    def __meta_call__(
            meta, arg0=None, /, *argn,  **kwargs
            ):
        if not argn:
            if arg0 is None:
                return _functools.partial(meta.decorate, **kwargs)
            else:
                return meta.decorate(arg0, **kwargs)
        _, __, body = args = (arg0, *argn)
        out = meta.__class_construct__(body)
        meta.__init__(out, *args, **kwargs)
        return out

    def __new__(meta, name, bases, ns, /, **kwargs):
        '''Called when using the type constructor directly, '''
        '''e.g. type(name, bases, namespace); '''
        '''__init__ is called implicitly.'''
        body = meta.__prepare__(name, bases, **kwargs)
        body.update(ns)
        return meta.__class_construct__(body)

    @classmethod
    def __class_construct__(meta, body: _ClassBody, /):
        return super().__new__(meta, *body.finalise())

    @property
    def __ptolemaic_class__(cls, /):
        return cls._get_ptolemaic_class()

    ### Initialising the class:

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(cls, *args, **kwargs)
        iscosmic = cls._clsiscosmic
        del cls._clsiscosmic
        if iscosmic:
            cls.__class_initialise__()

    @classmethod
    def _get_qualname(cls, /):
        try:
            corpus = cls.__corpus__
        except AttributeError:
            return cls.__relname__
        return corpus.__relname__ + '.' + cls.__relname__

    ### Storage:

    @property
    def taphonomy(cls, /):
        return _FOCUS.bureau.taphonomy

    ### Implementing the attribute-freezing behaviour for classes:

    @property
    def mutable(cls, /):
        return cls.__dict__['_clsmutable']

    @mutable.setter
    def mutable(cls, val, /):
        cls.mutable.toggle(val)

    # def __getattribute__(cls, name, /):
    #     try:
    #         name = type.__getattribute__(cls, '__mangled_names__')[name]
    #     except KeyError:
    #         pass
    #     return type.__getattribute__(cls, name)
        # try:
        #     return type.__getattribute__(cls, name)
        # except AttributeError:
        #     try:
        #         return type.__getattribute__(cls, '__class_altdict__')[name]
        #     except KeyError as exc:
        #         raise AttributeError from exc

    def __setattr__(cls, name, val, /):
        if cls.mutable:
            if not name.startswith('_'):
                cls.param_convert(val)
                try:
                    setname = val.__set_name__
                except AttributeError:
                    pass
                else:
                    setname(cls, name)
            super().__setattr__(name, val)
        else:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )

    def __delattr__(cls, name, /):
        if cls.mutable:
            super().__delattr__(name)
        else:
            raise AttributeError(
                "Cannot alter class attribute while immutable."
                )

    ### Aliases:

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
        cls = cls.__ptolemaic_class__
        try:
            return cls.__dict__['_clsepitaph']
        except KeyError:
            epi = cls.taphonomy.auto_epitaph(cls)
            corpus = cls.__corpus__
            if corpus is None:
                epi = cls.taphonomy.auto_epitaph(cls)
            else:
                epi = cls.taphonomy.getattr_epitaph(
                    corpus, cls.__relname__
                    )
            type.__setattr__(cls, '_clsepitaph', epi)
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

    @property
    def param_convert(cls, /):
        return _ptolemaic.convert


@_ptolemaic.Ptolemaic.register
class _EssenceBase_(metaclass=Essence):

    @classmethod
    def __class_set_name__(cls, owner, name, /):
        assert owner.mutable
        if cls.mutable:
            cls.__class_relname__ = name
            cls.__class_corpus__ = owner
            cls.__qualname__ = owner.__qualname__ + '.' + name
            owner.register_notion(cls)
        bound = _BoundObject(cls)
        type.__setattr__(owner, name, bound)
        bound.__set_name__(owner, name)

    @classmethod
    def __class_bound_get__(cls, instance: object, name: str, /):
        return cls

    @classmethod
    def __class_bound_owner_get__(cls, owner: type, name: str, /):
        return cls

    @classmethod
    def __class_bound_set__(cls, instance, name, value, /):
        raise AttributeError(
            f"Can't set attribute: {instance}, {name}"
            )

    @classmethod
    def __class_bound_delete__(cls, instance, name, /):
        raise AttributeError(
            f"Can't delete attribute: {instance}, {name}"
            )

    @classmethod
    def _class_register_notion(cls, other, /):
        if cls.mutable:
            cls._clsnotions.append(other)
        else:
            raise RuntimeError(
                "Cannot register a new notion "
                "after a class has been made immutable "
                "(i.e. after it has been completely initialised): "
                f"{cls}"
                )

    @classmethod
    def _class_register_organ(cls, other, /):
        if cls.mutable:
            cls._clsorgans.append(other)
        else:
            raise RuntimeError(
                "Cannot register a new organ "
                "after a class has been made immutable "
                "(i.e. after it has been completely initialised): "
                f"{cls}"
                )

    @classmethod
    def __class_initialise__(cls, /):
        cls.__class_init__()
        for inner in cls._clsnotions:
            inner.__class_initialise__()
        cls.mutable = False

    @classmethod
    def __class_init__(cls, /):
        pass

    @classmethod
    def _get_ptolemaic_class(cls, /):
        return cls


with Essence.mutable:
    Essence._defaultbasetyp = Essence.BaseTyp


###############################################################################
###############################################################################


    # @classmethod
    # def _yield_affixfiltered(
    #         meta, bases, ns, /, overname: str, prefix: str, suffix: str
    #         ):
    #     for base in reversed(bases):
    #         try:
    #             dct = type.__getattribute__(cls, overname)
    #         except AttributeError:
    #             continue
    #         yield from dct.items()
    #     for name, val in ns.items():
    #         if name.startswith(prefix) and name.endswith(suffix):
    #             stump = name.removeprefix(prefix).removesuffix(suffix)
    #             yield stump, dct[name]


#     ### Implementing mroclasses:

#     def _gather_mrobases(cls, name: str, /):
#         for base in cls.__bases__:
#             try:
#                 candidate = getattr(base, name)
#             except AttributeError:
#                 continue
#             try:
#                 yield candidate.__mroclass__
#             except AttributeError:
#                 yield candidate

#     @property
#     def __mroclass__(cls, /):
#         return cls.__dict__.get('_mroclass', cls.__ptolemaic_class__)

#     def _make_mroclass(cls, name: str, /):
#         bases = tuple(cls._gather_mrobases(name))
#         if not all(isinstance(base, Essence) for base in bases):
#             raise TypeError("All mroclass bases must be Essences.", bases)
#         if name in cls.__dict__:
#             homebase = cls.__dict__[name]
#             try:
#                 homebase = homebase.__mroclass__
#             except AttributeError:
#                 raise TypeError(homebase)
#             if not isinstance(homebase, Essence):
#                 raise TypeError(
#                     "All mroclass bases must be Essences.", homebase
#                     )
#             mrobasename = f"<mrobase_{name}>"
#             # setattr(cls, mrobasename, homebase)
#             if is_innerclass(homebase, cls):
#                 with homebase.mutable:
#                     homebase.__qualname__ = \
#                         f"{cls.__qualname__}.{mrobasename}"
#             bases = (homebase, *bases)
#         if not bases:
#             bases = (Essence.BaseTyp,)
#             # return
#         mrofusedname = f"<mrofused_{name}>"
#         ns = {
#             '_ptolemaic_contexts': (*cls.contexts, cls),
#             '__module__': cls.__module__,
#             '__qualname__': f"{cls.__qualname__}.{mrofusedname}",
#             }
#         fused = type(name, bases, ns)
#         # setattr(cls, mrofusedname, fused)
#         bases = (fused, *(
#             getattr(cls, oname)
#             for oname in fused.OVERCLASSES
#             if hasattr(cls, oname)
#             ))
#         ns = {
#             '_ptolemaic_owners': (*cls.contexts, cls),
#             '__module__': cls.__module__,
#             '__qualname__': f"{cls.__qualname__}.{name}",
#             '_mroclass': fused,
#             }
#         final = type(name, bases, ns)
#         setattr(cls, name, final)
#         try:
#             meth = final.__set_name__
#         except AttributeError:
#             pass
#         else:
#             meth(cls, name)
#         return final

#     def _add_mroclass(cls, name: str, /):
#         setattr(cls, name, cls._make_mroclass(name))

#     def _add_mroclasses(cls, /):
#         for name in cls.MROCLASSES:
#             cls._add_mroclass(name)

#     @property
#     def contexts(cls, _default=(), /):
#         return cls.__ptolemaic_class__.__dict__.get(
#             '_ptolemaic_contexts', _default
#             )

#     @property
#     def context(cls, /):
#         try:
#             return cls.contexts[-1]
#         except IndexError:
#             return None

#     @property
#     def truecontext(cls, /):
#         try:
#             return cls.contexts[0]
#         except IndexError:
#             return None


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
