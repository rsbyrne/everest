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


class Ptolemaic(_Essence):

    ### Handling dynamic class attributes like `.epitaph`:

    def __getattr__(cls, name, /):
        if name in cls.DYNATTRS:
            return getattr(cls, '_class_' + name)
        return super().__getattr__(name)

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


class PtolemaicBase(metaclass=Ptolemaic):

    MERGETUPLES = ('DYNATTRS',)
    DYNATTRS = (
        'epitaph', 'taphonomy', 'mutable', 'freezeattr',
        'hexcode', 'hashint', 'hashID', '_ptolemaic_class__'
        )

    __slots__ = (
        '_softcache', '_weakcache', '__weakref__', '_freezeattr',
        'finalised',
        )

    ### What happens when the class is called:

    @classmethod
    def create_object(cls, /):
        return cls.__new__(cls)

    @classmethod
    def instantiate(cls, /, *args, _softcache=None, _weakcache=None, **kwargs):
        obj = cls.create_object()
        obj.initialise(*args, _softcache=_softcache, _weakcache=_weakcache, **kwargs)
        obj.finalise()
        return obj

    def __init__(self, /):
        pass

    def initialise(self, /, *args, _softcache=None, _weakcache=None, **kwargs):
        self.finalised = False
        softcache = self._softcache = {}
        if not _softcache is None:
            softcache.update(_softcache)
        weakcache = self._weakcache = _weakref.WeakValueDictionary()
        if not _weakcache is None:
            weakcache.update(_weakcache)
        self.__init__(*args, **kwargs)

    def __finish__(self, /):
        pass

    def finalise(self, /):
        self.__finish__()
        self.finalised = True
        self.freezeattr.toggle(True)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)

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
