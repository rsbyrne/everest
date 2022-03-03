###############################################################################
''''''
###############################################################################


import weakref as _weakref

from everest.utilities import pretty as _pretty

from everest.primitive import Primitive as _Primitive

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.namespace import Namespace as _Namespace


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

    parent: Plexon

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        bound = super().parameterise(*args, **kwargs)
        if not isinstance(bound.arguments['parent'], Plexon):
            raise TypeError
        return bound

    @property
    def plex(self, /):
        return self.parent.plex


class GroupPlexon(Plexon):

    _req_slots__ = ('subs',)

    def __init__(self, /):
        super().__init__()
        self.subs = _weakref.WeakValueDictionary()

    def sub(self, /, name, *args, typ, **kwargs):
        if not issubclass(typ, SubPlexon):
            raise TypeError(typ)
        subs = self.subs
        try:
            out = subs[name]
        except KeyError:
            out = self.subs[name] = typ(self, *args, **kwargs)
        else:
            if not isinstance(out, typ):
                print(out)
                raise TypeError(type(out))
        return out


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