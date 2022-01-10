###############################################################################
''''''
###############################################################################


import collections as _collections
import functools as _functools
import types as _types
import inspect as _inspect
import weakref as _weakref

from everest.utilities import caching as _caching, reseed as _reseed

from everest.ptolemaic.essence import Essence as _Essence


def _sprite_get_epitaph(self, /):
    ptolcls = self._ptolemaic_class__
    return ptolcls.taphonomy.callsig_epitaph(ptolcls, *self.values())

@property
@_caching.soft_cache()
def _sprite_epitaph(self, /):
    return self.get_epitaph()

@property
def _sprite_hexcode(self, /):
    return self.epitaph.hexcode

@property
def _sprite_hashint(self, /):
    return self.epitaph.hashint

@property
def _sprite_hashID(self, /):
    return self.epitaph.hashID

@property
def _sprite_softcache(self, /):
    hashno = hash(self)
    try:
        return self._instancesoftcaches[hashno]
    except KeyError:
        out = self._instancesoftcaches[hashno] = {}
        return out

@property
def _sprite_weakcache(self, /):
    hashno = hash(self)
    try:
        return self._instanceweakcaches[hashno]
    except KeyError:
        out = self._instanceweakcaches[hashno] = {}
        return out

@property
def _sprite___ptolemaic_class__(self, /):
    return type(self)._ptolemaic_class__

@property
@_caching.soft_cache()
def _sprite_params(self, /):
    return _types.MappingProxyType({
        key: getattr(self, key) for key in self._fields
        })

def _sprite___del__(self, /):
    hashno = hash(self)
    for cache in (self._instancesoftcaches, self._instanceweakcaches):
        try:
            del cache[hashno]
        except KeyError:
            pass

def _sprite___repr__(self, /):
    valpairs = ', '.join(map('='.join, zip(
        (params := self.params),
        map(repr, params.values()),
        )))
    return f"<{self._ptolemaic_class__}({valpairs})>"

def _sprite__repr_pretty_(self, p, cycle):
    p.text('<')
    root = repr(self._ptolemaic_class__)
    if cycle:
        p.text(root + '{...}')
    elif not (kwargs := self.params):
        p.text(root + '()')
    else:
        with p.group(4, root + '(', ')'):
            kwargit = iter(kwargs.items())
            p.breakable()
            key, val = next(kwargit)
            p.text(key)
            p.text(' = ')
            p.pretty(val)
            for key, val in kwargit:
                p.text(',')
                p.breakable()
                p.text(key)
                p.text(' = ')
                p.pretty(val)
            p.breakable()
    p.text('>')

SPRITENAMESPACE = dict(
    get_epitaph=_sprite_get_epitaph,
    epitaph=_sprite_epitaph,
    hexcode=_sprite_hexcode,
    hashint=_sprite_hashint,
    hashID=_sprite_hashID,
    softcache=_sprite_softcache,
    weakcache=_sprite_weakcache,
    _ptolemaic_class__=_sprite___ptolemaic_class__,
    params=_sprite_params,
    __del__=_sprite___del__,
    __repr__=_sprite___repr__,
    _repr_pretty_=_sprite__repr_pretty_,
    )


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
    def pre_create_class(meta, name, bases, namespace, /):

        NamedTup = _collections.namedtuple(
            f"{name}_NamedTuple",
            (fields := namespace.get('__annotations__', {})),
            defaults=tuple(meta.yield_default_values(fields, namespace)),
            module=namespace['__module__'],
            )
        for nm in fields:
            if nm in namespace:
                del namespace[nm]
            
        bases = (*bases, NamedTup)

        namespace = SPRITENAMESPACE | namespace

        return name, bases, namespace

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._instancesoftcaches = {}
        cls._instanceweakcaches = {}
        callmeth = cls.__callmeth__ = cls.__new__.__get__(cls)
        cls.__signature__ = _inspect.signature(callmeth)

    @property
    def __call__(cls, /):
        return cls.__callmeth__


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
