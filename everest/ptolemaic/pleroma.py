###############################################################################
''''''
###############################################################################


import abc as _abc
import pickle as _pickle
from inspect import getmodule as _getmodule

from everest.utilities import caching as _caching, switch as _switch
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
    def taphonomy(meta, /):
        return _epitaph.TAPHONOMY

    def get_meta_epitaph(meta, /):
        return meta.taphonomy.auto_epitaph(meta)

    @property
    @_caching.soft_cache('_meta_softcache')
    def epitaph(meta, /):
        return meta.get_meta_epitaph()


class Pleromatic(_classtools.FreezableMeta, metaclass=Pleroma):

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
        if tuple(filter(basetyp.__subclasscheck__, bases)):
            return bases
        return (*bases, basetyp)

    @classmethod
    def _pleroma_construct(meta,
            name: str = None,
            bases: tuple = (),
            namespace: dict = None,
            ):
        if namespace is None:
            namespace = {}
        addspace = dict(__slots__=())
        if name is None:
            name = ''.join(base.__name__ for base in bases)
            if not name:
                raise ValueError(
                    "Must provide at least one "
                    "of either a class name or a tuple of bases."
                    )
        namespace = namespace | addspace
        bases = meta.process_bases(bases)
        out = _abc.ABCMeta.__call__(meta, name, bases, namespace)
        out.clsfreezeattr = True
        return out

    def _ptolemaic_isinstance__(cls, arg, /):
        return super().__instancecheck__(arg)

    def __instancecheck__(cls, arg, /):
        return cls._ptolemaic_isinstance__(arg)

    def _ptolemaic_getitem__(cls, arg, /):
        raise NotImplementedError

    def __getitem__(cls, arg, /):
        return cls._ptolemaic_getitem__(arg)

    def _ptolemaic_contains__(cls, arg, /):
        raise NotImplementedError

    def __contains__(cls, arg, /):
        return cls._ptolemaic_contains__(arg)


###############################################################################
###############################################################################
