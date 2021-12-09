###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref

from everest import classtools as _classtools
from everest.utilities import (
    caching as _caching,
    switch as _switch,
    )

from everest.ptolemaic.pleroma import Pleromatic as _Pleromatic


class Ptolemaic(metaclass=_Pleromatic):

    __slots__ = ('_softcache', '_weakcache', '__weakref__', '_freezeattr')

    ### Some aliases:

    @property
    def metacls(self, /):
        return type(self)._ptolemaic_class__.metacls

    @property
    def taphonomy(self, /):
        return type(self)._ptolemaic_class__.clstaphonomy

    ### What happens when the class is called:

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        obj = cls.__new__(cls, *args, **kwargs)
        obj._softcache = {}
        obj._weakcache = _weakref.WeakValueDictionary()
        obj.__init__(*args, **kwargs)
        obj.freezeattr = True
        return obj

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

    @freezeattr.setter
    def freezeattr(self, val, /):
        self._freezeattr.toggle(val)

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
        return None

    @_caching.soft_cache()
    def __repr__(self, /):
        content = f"({rep})" if (rep := self._repr()) else ''
        return f"<{self.__class__}{content}>"

    ### Rich comparisons to support ordering of objects:

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


###############################################################################
###############################################################################
