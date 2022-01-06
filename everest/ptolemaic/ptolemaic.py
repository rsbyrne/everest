###############################################################################
''''''
###############################################################################


import abc as _abc

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    reseed as _reseed,
    ) 

from everest.ptolemaic.essence import Essence as _Essence


class Ptolemaic(metaclass=_Essence):

    __slots__ = (
        '_softcache', '_weakcache', '__weakref__', '_freezeattr',
        'finalised',
        )

    ### Managing the instance cache:

    def update_cache(self, cache: dict, /):
        self._softcache.update(cache)

    def clear_cache(self, /):
        self._softcache.clear()

    def set_cache(self, cache, /):
        self.clear_cache()
        self.update_cache(cache)

    ### What happens when the class is called:

    @classmethod
    def __class_call__(cls, /, *args, _softcache=None, **kwargs):
        obj = cls.create_object()
        if _softcache is None:
            _softcache = dict()
        obj.initialise(*args, _softcache=_softcache, **kwargs)
        obj.finalise()
        return obj

    @classmethod
    def create_object(cls, /):
        return cls.__new__(cls)

    def __init__(self, /):
        pass

    def initialise(self, /, *args, _softcache, **kwargs):
        assert not hasattr(self, '__dict__'), type(self)
        self.finalised = False
        self._softcache = _softcache
        self.__init__(*args, **kwargs)

    def __finish__(self, /):
        pass

    def finalise(self, /):
        self.__finish__()
        self.finalised = True
        self.freezeattr.toggle(True)

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

    def _alt_setattr__(self, key, val, /):
        super().__setattr__(key, val)

    def __setattr__(self, key, val, /):
        if self.freezeattr:
            raise AttributeError(
                f"Setting attributes on an object of type {type(self)} "
                "is forbidden at this time; "
                f"toggle switch `.freezeattr` to override."
                )
        super().__setattr__(key, val)

    ### Representations:

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


class PtolemaicDat(Ptolemaic):

    __slots__ = ()

    ### Implementing serialisation:

    @property
    def taphonomy(self, /):
        return _Essence.BaseTyp.taphonomy

    @_abc.abstractmethod
    def get_epitaph(self, /):
        raise NotImplementedError

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        if not self.finalised:
            raise RuntimeError(
                "Cannot create epitaph before __finish__ is called.",
                )
        return self.get_epitaph()

    ### Representations:

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


class PtolemaicVar(Ptolemaic):

    __slots__ = ('identity',)

    reseed = _reseed.GLOBALRAND

    def initialise(self, /, *args, identity=None, **kwargs):
        if identity is None:
            identity = self.reseed.rdigits(12)
        self.identity = identity
        super().initialise(*args, **kwargs)
        
    def __setattr__(self, name, value, /):
        if name in self._var_slots__:
            self._alt_setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __hash__(self, /):
        return self.identity


###############################################################################
###############################################################################
