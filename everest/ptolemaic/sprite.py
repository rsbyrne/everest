###############################################################################
''''''
###############################################################################


import collections as _collections
import functools as _functools
import types as _types

from everest.utilities import caching as _caching, reseed as _reseed

from everest.ptolemaic.essence import Essence as _Essence


def _sprite_get_epitaph(self, /):
    clas = type(self)
    clascache = clas._instancecaches
    try:
        cache = clascache[self]
    except KeyError:
        cache = clascache[self] = _types.SimpleNamespace()
    else:
        try:
            return cache.epitaph
        except AttributeError:
            pass
    epitaph = cache.epitaph = clas.taphonomy.callsig_epitaph(clas, *self)
    return epitaph

def _sprite_get_hexcode(self, /):
    return self.epitaph.hexcode

def _sprite_get_hashint(self, /):
    return self.epitaph.hashint

def _sprite_get_hashID(self, /):
    return self.epitaph.hashID


class Sprite(_Essence):

    @classmethod
    def yield_default_values(meta, fields, namespace, /):
        for field in (fieldit := iter(fields)):
            if field in namespace:
                yield namespace[field]
                break
        else:
            return
        for field in fieldit:
            try:
                yield namespace[field]
            except KeyError as exc:
                raise TypeError(
                    f"Non-default field cannot follow default: {field}"
                    ) from exc

    @classmethod
    def process_bases(meta, name, bases, namespace, /):
        NamedTup = _collections.namedtuple(
            f"{name}_NamedTuple",
            (fields := namespace.get('__annotations__', {})),
            defaults=tuple(meta.yield_default_values(fields, namespace)),
            module=namespace['__module__'],
            )
        return super().process_bases(name, (*bases, NamedTup), namespace)

    @classmethod
    def process_namespace(meta, name, bases, namespace, /):
        namespace = super().process_namespace(name, bases, namespace)
        namespace.update(
            epitaph = property(_sprite_get_epitaph),
            hexcode = property(_sprite_get_hexcode),
            hashint = property(_sprite_get_hashint),
            hashID = property(_sprite_get_hashID),
            )
        return namespace

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._instancecaches = {}
        cls.construct = _functools.partial(cls.__new__, cls)

    @property
    def __call__(cls, /):
        return cls.construct


###############################################################################
###############################################################################


# class ClassCacheProperty:

#     __slots__ = ('name', 'cache', 'meth', 'cachename')

#     def __init__(self, meth, cachename, /):
#         self.meth, self.cachename = meth, cachename

#     def __set_name__(self, owner, name, /):
#         self.name = name
#         chnm = self.cachename
#         try:
#             self.cache = getattr(owner, chnm, {})
#         except AttributeError:
#             self.cache = getattr(owner, chnm) = {}

#     def __get__(self, instance, /):
#         name, cache = self.name, self.cache
#         hashval = hash(instance)
#         try:
#             icache = cache[hashval]
#         except KeyError:
#             icache = cache[hashval] = _weakref.WeakValueDictionary()
#         try:
#             return icache[name]
#         except KeyError:
#             val = icache[name] = self.meth(instance)
#             return val


# def classcache_property(cachename):
#     return _functools.partial(ClassCacheProperty, cachename)
