###############################################################################
''''''
###############################################################################


import weakref as _weakref

from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.diict import (
    Namespace as _Namespace,
    WeakNamespace as _WeakNamespace,
    )


class Attrs(_Namespace):

    def _set_val(self, name, val, /):
        if isinstance(val, _Primitive):
            super()._set_val(name, val)
        else:
            raise TypeError(type(val))


class Plexon(metaclass=_Essence):

    MERGETUPLES = ('_req_slots__',)

    _req_slots__ = ('attrs',)

    def __init__(self, /):
        super().__init__()
        self.attrs = Attrs()


class SubPlexon(Plexon):

    _req_slots__ = ('parent',)

    def __init__(self, /, parent, *args, **kwargs):
        if not isinstance(parent, Plexon):
            raise TypeError(type(parent))
        self.parent = parent
        super().__init__(*args, **kwargs)

    @property
    def plex(self, /):
        return self.parent.plex


class Subs(_WeakNamespace):

    _req_slots__ = ('owner',)

    def __init__(self, owner, /):
        super().__init__()
        self.owner = _weakref.proxy(owner)

    def _set_val(self, name, val, /):
        if name in self:
            raise ValueError(name)
        if isinstance(val, SubPlexon):
            if val.parent != self.owner:
                raise ValueError(val)
            super()._set_val(name, val)
        else:
            raise TypeError(type(val))


class GroupPlexon(Plexon):

    _req_slots__ = ('subs',)

    def __init__(self, /):
        super().__init__()
        self.subs = Subs(self)

    def sub(self, /, name, *args, typ, **kwargs):
        if not issubclass(typ, SubPlexon):
            raise TypeError(typ)
        new = typ(self, *args, **kwargs)
        setattr(self.subs, name, new)
        return new

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__qualname__
        self.subs._repr_pretty_(p, cycle, root=root)


###############################################################################
###############################################################################


#     def __getattr__(self, name, /):
#         try:
#             return super().__getattr__(name)
#         except AttributeError as exc:
#             if name in ('_content_', 'subs'):
#                 raise exc
#             return getattr(self.subs, name)

#     def __setattr__(self, name, val, /):      
#         try:
#             super().__setattr__(name, val)
#         except TypeError:
#             setattr(self.subs, name, val)

#     def __delattr__(self, name, /):      
#         try:
#             super().__delattr__(name, val)
#         except AttributeError:
#             delattr(self.subs, name)