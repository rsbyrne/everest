###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref

from everest.utilities import (
    caching as _caching,
    switch as _switch,
    format_argskwargs as _format_argskwargs,
    )

from everest.ptolemaic.essence import Essence as _Essence


class Ousia(_Essence):
    '''
    The metaclass of all classes that can be instantiated.
    '''

    ### Handling dynamic class attributes like `.epitaph`:

    def __getattribute__(cls, name, /):
        if name in type.__getattribute__(cls, 'DYNATTRS'):
            try:
                return getattr(cls, '_class_' + name)
            except AttributeError:
                pass
        return type.__getattribute__(cls, name)

    @property
    def _class__ptolemaic_class__(cls, /):
        return super()._ptolemaic_class__

    @property
    def _class_epitaph(cls, /):
        return super().epitaph

    @property
    def _class_taphonomy(cls, /):
        return super().taphonomy

    @property
    def _class_mutable(cls, /):
        return super().mutable

    @property
    def _class_freezeattr(cls, /):
        return super().freezeattr

    @property
    def _class_hexcode(cls, /):
        return super().hexcode

    @property
    def _class_hashint(cls, /):
        return super().hashint

    @property
    def _class_hashID(cls, /):
        return super().hashID


class OusiaBase(metaclass=Ousia):
    '''
    The class of all classes that can be instantiated.
    '''

    MERGETUPLES = ('DYNATTRS',)
    DYNATTRS = (
        'epitaph', 'taphonomy', 'mutable', 'freezeattr',
        'hexcode', 'hashint', 'hashID', '_ptolemaic_class__',
        )

    __slots__ = (
        '_softcache', '_weakcache', '__weakref__', '_freezeattr',
        'finalised',
        )

    ### What happens when the class is called:

    def update_cache(self, cache: dict, /):
        self._softcache.update(cache)

    def clear_cache(self, /):
        self._softcache.clear()

    def set_cache(self, cache, /):
        self.clear_cache()
        self.update_cache(cache)

    @classmethod
    def create_object(cls, /):
        return cls.__new__(cls)

    def __init__(self, /):
        pass

    def initialise(self, /, *args, _softcache=None, **kwargs):
        self.finalised = False
        self._softcache = dict()
        if _softcache is not None:
            self.update_cache(_softcache)
        self.__init__(*args, **kwargs)

    def __finish__(self, /):
        pass

    def finalise(self, /):
        self.__finish__()
        self.finalised = True
        self.freezeattr.toggle(True)

    @classmethod
    def __class_call__(cls, /, *args, _softcache=None, **kwargs):
        obj = cls.create_object()
        obj.initialise(*args, _softcache=_softcache, **kwargs)
        obj.finalise()
        return obj

    ### Some aliases:

    @property
    def _ptolemaic_class__(self, /):
        return self.__class__._ptolemaic_class__

    @property
    def taphonomy(self, /):
        return self._ptolemaic_class__.taphonomy

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

    ### Implementing serialisation:

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

    def _repr(self, /):
        return ''

    def __repr__(self, /):
        return f"<{self._ptolemaic_class__}({self._repr()})>"

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
