###############################################################################
''''''
###############################################################################


import abc as _abc

import inspect as _inspect
import weakref as _weakref

from everest.utilities import (
    caching as _caching,
    reseed as _reseed,
    )
from everest.utilities.switch import Switch as _Switch
from everest.exceptions import (
    FrozenAttributesException as _FrozenAttributesException
    )

from .essence import Essence as _Essence


class ConcreteMeta:

    @classmethod
    def pre_create_class(meta, name, bases, namespace, /):
        return name, bases, namespace

    @classmethod
    def __meta_call__(meta, basecls, /):
        assert not hasattr(basecls, 'Construct')
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if isinstance(basecls, ConcreteMeta):
            raise TypeError("Cannot subclass a Concrete type.")
        return super().__class_construct__(*basecls.pre_create_concrete())

    @property
    def _ptolemaic_class__(cls, /):
        return cls._basecls

    @property
    def __signature__(cls, /):
        return cls._ptolemaic_class__.__signature__

    def __call__(cls, /, *args, **kwargs):
        return cls._ptolemaic_class__.__new__(cls, *args, **kwargs)

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
    def Concrete(cls, /):
        try:
            return cls.__dict__['_Concrete']
        except KeyError:
            with cls.mutable:
                out = cls._Concrete = cls.ConcreteMeta(cls)
            return out

#     ConcreteAbstract = ConcreteAbstract


class OusiaBase(metaclass=Ousia):

    MERGETUPLES = ('_req_slots__',)
    _req_slots__ = (
        '_softcache', '_weakcache', '__weakref__', 'freezeattr',
        )

    @classmethod
    def corporealise(cls, /):
        obj = cls.Concrete()
        object.__setattr__(obj, 'freezeattr', _Switch(False))
        return obj

    def initialise(self, /, *args, **kwargs):
        self._ptolemaic_class__.__init__(self, *args, **kwargs)
        self.freezeattr.toggle(True)

    @classmethod
    def instantiate(cls, /, *args, **kwargs):
        obj = cls.corporealise()
        obj.initialise(*args, **kwargs)
        return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)

    ### Configuring the concrete class:

    @classmethod
    def pre_create_concrete(cls, /):
        name = f"Concrete_{cls._ptolemaic_class__.__name__}"
        bases = (cls,)
        namespace = dict(
            __slots__=cls._req_slots__,
            _basecls=cls,
            __class_init__=lambda: None,
            )
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
            with self.mutable:
                out = self._weakcache = _weakref.WeakValueDictionary()
            return out

    ### Some aliases:

    @property
    def _ptolemaic_class__(self, /):
        return self.__class__._ptolemaic_class__

    @property
    def taphonomy(self, /):
        return self._ptolemaic_class__.taphonomy

    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def mutable(self, /):
        return self.freezeattr.as_(False)

    def __setattr__(self, name, val, /):
        try:
            check = self.freezeattr
        except AttributeError:
            pass
        else:
            if check:
                raise _FrozenAttributesException(
                    f"Setting attributes "
                    f"on an object of type {type(self)} "
                    "is forbidden at this time; "
                    f"toggle switch `.freezeattr` to override."
                    )
        object.__setattr__(self, name, val)

    def __delattr__(self, name, /):
        try:
            check = self.freezeattr
        except AttributeError:
            pass
        else:
            if check:
                raise _FrozenAttributesException(
                    f"Deleting attributes "
                    f"on an object of type {type(self)} "
                    "is forbidden at this time; "
                    f"toggle switch `.freezeattr` to override."
                    )
        object.__delattr__(self, name)

    ### Representations:

    def _root_repr(self, /):
        ptolcls = self._ptolemaic_class__
        return ':'.join(map(str,
            (type(ptolcls).__qualname__, ptolcls.__qualname__, id(self))
            ))

    @property
    @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    def _content_repr(self, /):
        return ''

    @property
    @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def __repr__(self, /):
        return f"<{self.rootrepr}>"

    @_caching.soft_cache()
    def __hash__(self, /):
        return _reseed.rdigits(12)

    @property
    @_abc.abstractmethod
    def epitaph(self, /):
        raise NotImplementedError

    ### Rich comparisons to support ordering of objects:

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


###############################################################################
###############################################################################
