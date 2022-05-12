###############################################################################
''''''
###############################################################################


import abc as _abc

import inspect as _inspect
import weakref as _weakref

from everest.utilities import (
    caching as _caching,
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
    def __ptolemaic_class__(cls, /):
        return cls._basecls

    @property
    def __signature__(cls, /):
        return cls.__ptolemaic_class__.__signature__

    def __call__(cls, /):
        raise AttributeError

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

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with cls.mutable:
            cls.Concrete = cls.ConcreteMeta(cls)


class OusiaBase(metaclass=Ousia):

    MERGETUPLES = ('__req_slots__',)
    __req_slots__ = (
        '__weakref__',
        'softcache', 'weakcache', 'freezeattr',
        )

    @classmethod
    def corporealise(cls, /):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        object.__setattr__(obj, 'freezeattr', _Switch(False))
        object.__setattr__(obj, 'softcache', {})
        object.__setattr__(obj, 'weakcache', _weakref.WeakValueDictionary())
        return obj

    @classmethod
    def instantiate(cls, /, *args, **kwargs):
        obj = cls.corporealise()
        obj.__init__(*args, **kwargs)
        obj.freezeattr.toggle(True)
        return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)

    ### Configuring the concrete class:

    @classmethod
    def pre_create_concrete(cls, /):
        name = f"Concrete_{cls.__ptolemaic_class__.__name__}"
        bases = (cls,)
        namespace = dict(
            __slots__=cls.__req_slots__,
            _basecls=cls,
            __class_init__=lambda: None,
            )
        return name, bases, namespace

    ### Some aliases:

    @property
    def __ptolemaic_class__(self, /):
        return self.__class__.__ptolemaic_class__

    @property
    def taphonomy(self, /):
        return self.__ptolemaic_class__.taphonomy

    ### Storage:

    @property
    @_caching.weak_cache()
    def tab(self, /):
        return _bureau.request_tab(self)

    @property
    @_caching.weak_cache()
    def tray(self, /):
        return _bureau.request_tray(self)

    @property
    @_caching.weak_cache()
    def drawer(self, /):
        return _bureau.request_drawer(self)

    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def mutable(self, /):
        return self.freezeattr.as_(False)

    def __process_attr__(self, val, /):
        return val

    def __setattr__(self, name, val, /):
        if name in self.__slots__:
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
                val = self.__process_attr__(val)
        object.__setattr__(self, name, val)

    def __delattr__(self, name, /):
        if name in self.__slots__:
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
        ptolcls = self.__ptolemaic_class__
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
    def contentrepr(self, /):
        return self._content_repr()

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def __repr__(self, /):
        return f"<{self.rootrepr}>"

    def __hash__(self, /):
        return id(self)

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    def epitaph(self, /):
        return self.make_epitaph()

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def __hash__(self, /):
        return self.hashint

    ### Rich comparisons to support ordering of objects:

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


###############################################################################
###############################################################################
