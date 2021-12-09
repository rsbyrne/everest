###############################################################################
''''''
###############################################################################


import abc as _abc
import pickle as _pickle
import weakref as _weakref
from inspect import getmodule as _getmodule

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    FrozenMap as _FrozenMap,
    )
from everest import epitaph as _epitaph
from everest.primitive import Primitive as _Primitive
from everest import classtools as _classtools


class Pleroma(type):

    def _pleroma_contains__(meta, _, /):
        raise NotImplementedError

    def __contains__(meta, arg, /):
        return meta._pleroma_contains__(arg)

    def _pleroma_getitem__(meta, arg, /):
        raise NotImplementedError

    def __getitem__(meta, arg, /):
        return meta._pleroma_getitem__(arg)

    def _pleroma_setitem__(meta, key, val, /):
        raise NotImplementedError

    def __setitem__(meta, key, val, /):
        return meta._pleroma_setitem__(key, val)

    def _pleroma_init__(meta, /):
        raise NotImplementedError

    def __init__(meta, /, *args, **kwargs):
        with meta.metamutable:
            meta._meta_softcache = {}
            super().__init__(*args, **kwargs)
            meta._pleroma_init__()

    @property
    def metafreezeattr(meta, /):
        try:
            return meta.__dict__['_metafreezeattr']
        except KeyError:
            super().__setattr__(
                '_metafreezeattr', switch := _switch.Switch(True)
                )
            return switch

    @property
    def metamutable(meta, /):
        return meta.metafreezeattr.as_(False)

    @metafreezeattr.setter
    def metafreezeattr(meta, val, /):
        meta._metafreezeattr.toggle(val)

    def __setattr__(meta, key, val, /):
        if meta.metafreezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(meta)} "
                "is forbidden at this time; "
                f"toggle switch `.metafreezeattr` to override."
                )
        super().__setattr__(key, val)

    def _pleroma_construct(meta, /):
        raise NotImplementedError

    def __call__(meta, /, *args, **kwargs):
        return meta._pleroma_construct(*args, **kwargs)

    @property
    def pleromabases(meta, /):
        return tuple(
            base for base in meta.__mro__ if isinstance(base, Pleroma)
            )

    def get_basetyp(meta, /):
        module = _getmodule(meta)
        try:
            return eval(f"{meta.__name__}Base", {}, module.__dict__)
        except NameError:
            bases = meta.pleromabases[1:]
            if bases:
                return Pleroma.get_basetyp(bases[0])
            return object

    @property
    def BaseTyp(meta, /):
        return meta.get_basetyp()

    @property
    def metataphonomy(meta, /):
        return _epitaph.TAPHONOMY


class Pleromatic(_abc.ABCMeta, metaclass=Pleroma):

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

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(type(cls), cls, *args, **kwargs)
        clsdct = cls.__dict__
        if (annokey := '__annotations__') in clsdct:
            anno = clsdct[annokey]
        else:
            setattr(cls, annokey, anno := {})
        if (extkey := '_extra_annotations__') in clsdct:
            anno.update(clsdct[extkey])
        setattr(cls, annokey, _FrozenMap(anno))

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


#     def get_meta_epitaph(meta, /):
#         return meta.taphonomy.auto_epitaph(meta)

#     @property
#     @_caching.soft_cache('_meta_softcache')
#     def epitaph(meta, /):
#         return meta.get_meta_epitaph()


###############################################################################
###############################################################################
