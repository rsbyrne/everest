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

from everest.ptolemaic.essence import Essence as _Essence


class ConcreteMeta:

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):
        return name, bases, namespace

    @classmethod
    def __class_construct__(meta, basecls):
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if issubclass(type(basecls), ConcreteMeta):
            raise TypeError("Cannot subclass a Concrete type.")
        return super().__class_construct__(
            basecls.concrete_name,
            basecls.concrete_bases,
            basecls.concrete_namespace,
            )

    def __init__(cls, /, *args, **kwargs):
        _abc.ABCMeta.__init__(type(cls), cls, *args, **kwargs)

    def __class_init__(cls, /):
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


class Ousia(_Essence):

    @classmethod
    def concretemeta_namespace(meta, /):
        return {}

    @classmethod
    def __meta_init__(meta, /):
        super().__meta_init__()
        if not issubclass(meta, ConcreteMeta):
            meta.ConcreteMeta = type(
                f"{meta.__name__}_ConcreteMeta",
                (ConcreteMeta, meta),
                meta.concretemeta_namespace(),
                )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.Concrete = cls.ConcreteMeta(cls)

    @property
    def __signature__(cls, /):
        return _inspect.signature(cls.Concrete.__init__)

    @property
    def concrete_slots(cls, /):
        return cls.get_concrete_slots()

    @property
    def concrete_name(cls, /):
        return cls.get_concrete_name()

    @property
    def concrete_bases(cls, /):
        return tuple(cls.get_concrete_bases())

    @property
    def concrete_namespace(cls, /):
        return cls.get_concrete_namespace()

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

    ### Configuring the concrete class:

    @classmethod
    def get_concrete_name(cls, /):
        return f"Concrete_{cls._ptolemaic_class__.__name__}"

    @classmethod
    def get_concrete_bases(cls, /):
        yield cls

    @classmethod
    def get_concrete_slots(cls, /):
        return tuple(
            name for name in cls._req_slots__
            if not hasattr(cls, name)
            )

    @classmethod
    def get_concrete_namespace(cls, /):
        return dict(
            __slots__=cls.concrete_slots,
            _basecls=cls,
            __class_init__=lambda: None,
            )

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

    @_caching.soft_cache()
    def __hash__(self, /):
        return _reseed.rdigits(12)

    def _repr(self, /):
        return str(hash(self))

    def __repr__(self, /):
        return f"<{type(self)}({self._repr()})>"

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


#         if not issubclass(cls.ConcreteBase, ConcreteAbstract):
#             raise TypeError(
#                 "ConcreteBase class must inherit from ConcreteAbstract."
#                 )


# class ConcreteAbstractMeta(_abc.ABCMeta):

#     def __new__(meta, name, bases, namespace, /):
#         if name == 'ConcreteAbstract':
#             return super().__new__(meta, name, bases, namespace)
#         if '__slots__' not in namespace:
#             namespace['__slots__'] = ()
#         bases = tuple(base for base in bases if base is not ConcreteAbstract)
#         out = type(name, bases, namespace)
#         ConcreteAbstract.register(out)
#         return out


# class ConcreteAbstract(metaclass=ConcreteAbstractMeta):
#     ...


#     MERGETUPLES = ('_req_slots__', '_var_slots__')
#     _req_slots__ = ()
#     _var_slots__ = ()

#     MROCLASSES = ('ConcreteBase', 'VarBase', 'DatBase')

#     @classmethod
#     def get_concrete_name(cls, /):
#         return f"{'Var' if cls._var_slots__ else 'Dat'}_{cls.__name__}"

#     @classmethod
#     def get_concrete_bases(cls, /):
#         if cls._var_slots__:
#             yield cls.VarBase
#             yield cls.ConcreteBase
#             yield _ptolemaic.PtolemaicVar
#         else:
#             yield cls.DatBase
#             yield cls.ConcreteBase
#             yield _ptolemaic.PtolemaicDat
#         yield cls

#     @classmethod
#     def get_slots(cls, /):
#         return tuple(sorted(set(
#             name for name in _itertools.chain(
#                 cls._req_slots__,
#                 cls._var_slots__,
#                 )
#             if not hasattr(cls, name)
#             )))


#         slots = tuple(sorted(set(_itertools.chain(
#             basecls._req_slots__, basecls._var_slots__
#             ))))

#     class VarBase:

#         __slots__ = ()

#     class DatBase:

#         __slots__ = ()

#     @property
#     def __call__(cls, /):
#         return cls.__class_call__

#     def create_ur_class(cls, name, /):
#         return cls.ConcreteMeta.create_class(
#             f"{cls.__name__}{name}",
#             (getattr(cls, f"{name}Base"), cls.Concrete),
#             {'__slots__': ()}
#             )

#         cls.Var = cls.create_ur_class('Var')
#         cls.Dat = cls.create_ur_class('Dat')

#     MERGETUPLES = ('_req_slots__', '_var_slots__')

#     _var_slots__ = ()

#     MROCLASSES = ('ConcreteBase', 'VarBase', 'DatBase')

#     @classmethod
#     def __class_call__(cls, /, *args, **kwargs):
#         constructor = cls.Var if cls._var_slots__ else cls.Dat
#         return constructor.__class_call__(*args, **kwargs)

#     class VarBase(_ur.Var):

#         __slots__ = ()

#         def __setattr__(self, name, value, /):
#             if name in self._var_slots__:
#                 self._alt_setattr__(name, value)
#             else:
#                 super().__setattr__(name, value)

#     class DatBase(_ur.Dat):

#         __slots__ = ()


# class Nullary(metaclass=Ousia):

#     @classmethod
#     def __class_call__(cls, /, *, _softcache=None):
#         try:
#             return cls.weakcache['instance']
#         except KeyError:
#             instance = super().__class_call__(_softcache=_softcache)
#             cls.weakcache['instance'] = instance
#             return instance

#     class ConcreteBase:

#         @classmethod
#         def __class_call__(cls, /, *, _softcache=None):
#             return cls.Concrete(_softcache=_softcache)


# class Monument(metaclass=Ousia):

#     @classmethod
#     def __class_init__(cls, /):
#         cls.monumentname = cls.__name__.upper()

#     def __finish__(self, /):
#         with (kls := self._ptolemaic_class__).mutable:
#             kls.Concrete = lambda: self

#     class ConcreteBase:

#         __slots__ = ()

#         @classmethod
#         def construct(cls, /):
#             return super().construct()

#         def get_epitaph(self, /):
#             ptolclass = self._ptolemaic_class__
#             return self.taphonomy.custom_epitaph(
#                 f"$a.{ptolclass.monumentname}",
#                 a=ptolclass.__module__,
#                 )

#         def __repr__(self, /):
#             return self._ptolemaic_class__.monumentname