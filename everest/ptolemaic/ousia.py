###############################################################################
''''''
###############################################################################


import abc as _abc
import inspect as _inspect
import types as _types

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    reseed as _reseed,
    )
from everest.incision import IncisionHandler as _IncisionHandler

from everest.ptolemaic.essence import Essence as _Essence


class ConcreteMeta:

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):
        return name, bases, namespace

    @classmethod
    def __class_construct__(meta, basecls):
        assert not hasattr(basecls, 'Construct')
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if isinstance(basecls, ConcreteMeta):
            raise TypeError("Cannot subclass a Concrete type.")
        return super().__class_construct__(*basecls.pre_create_concrete())

    def __class_deep_init__(cls, /):
        pass

    @property
    def _ptolemaic_class__(cls, /):
        return cls._basecls

    @property
    def __signature__(cls, /):
        return cls._ptolemaic_class__.__signature__

    @property
    def __call__(cls, /, *_, **__):
        raise NotImplementedError

    @classmethod
    def __meta_init__(meta, /):
        pass


class Ousia(_Essence):

    @classmethod
    def concretemeta_namespace(meta, /):
        return {}

    @classmethod
    def __meta_init__(meta, /):
        super().__meta_init__()
        meta.ConcreteMeta = type(
            f"{meta.__name__}_ConcreteMeta",
            (ConcreteMeta, meta),
            meta.concretemeta_namespace(),
            )

    @property
    def __signature__(cls, /):
        return _inspect.signature(cls.Concrete.__init__)

    @property
    def Concrete(cls, /):
        try:
            return cls.__dict__['_Concrete']
        except KeyError:
            with cls.mutable:
                out = cls._Concrete = cls.ConcreteMeta(cls)
            return out

    def __call__(cls, /, *args, **kwargs):
        obj = object.__new__(cls.Concrete)
        obj.__init__(*args, **kwargs)
        obj.freezeattr.toggle(True)
        return obj

#     ConcreteAbstract = ConcreteAbstract


class OusiaBase(metaclass=Ousia):

    MERGETUPLES = ('_req_slots__',)

    _req_slots__ = (
        '_softcache', '_weakcache', '__weakref__', '_freezeattr',
        'finalised',
        )

    def __new__(cls, /, *_, **__):
        raise TypeError

#     @classmethod
#     def __choret_decorate__(cls, choret, /):
#         if '_Concrete' in cls.__dict__:
#             raise TypeError(f"Too late to decorate class! {cls}, {choret}")
#         with cls.mutable:
#             cls.Choret = choret
#             cls._ptolemaic_choret_decorated_ = True

    ### Configuring the concrete class:

    @classmethod
    def pre_create_concrete(cls, /):

        name = f"Concrete_{cls._ptolemaic_class__.__name__}"

        bases = [cls,]
#         if getattr(cls, '_ptolemaic_choret_decorated_', False):
#             bases.append(_IncisionHandler)
        bases = tuple(bases)

        slots = tuple(
            name for name in cls._req_slots__
            if not hasattr(cls, name)
            )

        namespace = dict(
            __slots__=cls._req_slots__,
            _basecls=cls,
            __class_init__=lambda: None,
            )
#         if getattr(cls, '_ptolemaic_choret_decorated_', False):
#             namespace.update(
#                 cls.__dict__['__incision_manager__'].decoratemeths
#                 )

        return name, bases, namespace

    ### Managing the instance cache:

    @property
    def softcache(self, /):
        try:
            return self._softcache
        except AttributeError:
            with self.mutable:
                out = self._softcache = {}
            return out

    @property
    def weakcache(self, /):
        try:
            return self._weakcache
        except AttributeError:
            out = self._weakcache = _weakref.WeakValueDictionary()
            return out

    ### Some aliases:

    @property
    def _ptolemaic_class__(self, /):
        return self.__class__._ptolemaic_class__

    @property
    def taphonomy(self, /):
        return self._ptolemaic_class__.taphonomy

    ### Class instantiation:

    def __init__(self, /):
        pass

    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def freezeattr(self, /):
        try:
            return self._freezeattr
        except AttributeError:
            super().__setattr__(
                '_freezeattr', switch := _switch.Switch(False)
                )
            return switch

    @property
    def mutable(self, /):
        return self.freezeattr.as_(False)

    def _alt_setattr__(self, name, val, /):
        super().__setattr__(name, val)

    def __setattr__(self, name, val, /):
        if self.freezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(self)} "
                "is forbidden at this time; "
                f"toggle switch `.freezeattr` to override."
                )
        super().__setattr__(name, val)

    def _alt_delattr__(self, name, /):
        super().__delattr__(name)

    def __delattr__(self, name, /):
        if self.freezeattr:
            raise AttributeError(
                f"Deleting attributes on an object of type {type(self)} "
                "is forbidden at this time; "
                f"toggle switch `.freezeattr` to override."
                )
        super().__delattr__(name)

    ### Representations:

    def _repr(self, /):
        return ''

    def __repr__(self, /):
        return f"<{type(self)}:{id(self)}({self._repr()})>"

    def __str__(self, /):
        return self.__repr__()

    ### Rich comparisons to support ordering of objects:

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


###############################################################################
###############################################################################
