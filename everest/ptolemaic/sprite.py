###############################################################################
''''''
###############################################################################


import collections as _collections
import functools as _functools
import types as _types
import inspect as _inspect
import weakref as _weakref
import abc as _abc

from everest.utilities import (
    caching as _caching,
    reseed as _reseed,
    FrozenMap as _FrozenMap,
    )

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
    return self._basecls

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

@property
def _sprite___getitem__(self, /):
    return super().__getitem__

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

    def get_fields(cls, /):
        empty = {}
        out = {}
        for base in reversed(cls.__mro__):
            out.update(base.__dict__.get('__annotations__', empty))
        return out

    def get_default_values(cls, fields, /):
        out = _collections.deque()
        for field in (fieldit := iter(fields)):
            for base in reversed(cls.__mro__):
                try:
                    out.append(base.__dict__[field])
                    break
                except KeyError:
                    pass
            else:
                if out:
                    raise TypeError(
                        f"Non-default field cannot follow default: {field}"
                        ) from exc
        return tuple(out)

    def get_concrete_class(cls, /):
        ConcreteBase = _collections.namedtuple(
            f"{cls}_NamedTuple",
            fields := cls.get_fields(),
            defaults=cls.get_default_values(fields),
#             module=namespace['__module__'],
            )
        out = type(cls).create_class_object(
            f"Concrete_{cls.__name__}",
            (cls, ConcreteBase),
            dict(_basecls=cls) | SPRITENAMESPACE,
            )
        out.__class_pre_init__(out.__name__, out.__bases__, {})
        out.freezeattr.toggle(True)
        return out

    def __class_deep_init__(cls, /):
        super().__class_deep_init__()
        cls._instancesoftcaches = {}
        cls._instanceweakcaches = {}
        Concrete = cls.Concrete = cls.get_concrete_class()
        callmeth = cls.__callmeth__ = Concrete.__new__.__get__(Concrete)
        cls.__signature__ = _inspect.signature(callmeth)

    @property
    def fields(cls, /):
        return cls.Concrete._fields

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
