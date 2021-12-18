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


class PtolemaicMeta(_Essence):
    ...


class Ptolemaic(metaclass=PtolemaicMeta):

    __slots__ = (
        '_softcache', '_weakcache', '__weakref__', '_freezeattr',
        'finalised',
        )

    ### What happens when the class is called:

    def __init__(self, /):
        self.finalised = False
        self._softcache = {}
        self._weakcache = _weakref.WeakValueDictionary()

    @classmethod
    def create_object(cls, /):
        return cls.__new__(cls)

    @classmethod
    def instantiate(cls, /, *args, **kwargs):
        obj = cls.create_object()
        obj.__init__(*args, **kwargs)
        return obj

    def __finish__(self, /):
        self.finalised = True
        self.freezeattr.toggle(True)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        obj = cls.instantiate(*args, **kwargs)
        obj.__finish__()
        return obj

    ### Some aliases:

    @property
    def metacls(self, /):
        return self.__class__._ptolemaic_class__.metacls

    @property
    def taphonomy(self, /):
        return self.__class__._ptolemaic_class__.clstaphonomy

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
        return f"<{self.__class__}({self._repr()})>"

    ### Rich comparisons to support ordering of objects:

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


###############################################################################
###############################################################################
