###############################################################################
''''''
###############################################################################


from collections import namedtuple as _namedtuple
import functools as _functools
import types as _types
from inspect import Signature as _Signature, Parameter as _Parameter, _empty
import weakref as _weakref
import abc as _abc

from everest.utilities import (
    caching as _caching,
    reseed as _reseed,
    FrozenMap as _FrozenMap,
    )
from everest.ur import Dat as _Dat

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic import exceptions as _exceptions


def _sprite_get_epitaph(self, /):
    ptolcls = self._ptolemaic_class__
    return ptolcls.taphonomy.callsig_epitaph(
        ptolcls, *self.params.values()
        )

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
    num = id(self)
    try:
        return self._instancesoftcaches[num]
    except KeyError:
        out = self._instancesoftcaches[num] = {}
        return out

@property
def _sprite_weakcache(self, /):
    num = id(self)
    try:
        return self._instanceweakcaches[num]
    except KeyError:
        out = self._instanceweakcaches[num] = {}
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
    num = id(self)
    for cache in (self._instancesoftcaches, self._instanceweakcaches):
        try:
            del cache[num]
        except KeyError:
            pass

def _sprite___repr__(self, /):
    valpairs = ', '.join(map('='.join, zip(
        (params := self.params),
        map(repr, params.values()),
        )))
    return f"<{self._ptolemaic_class__}({valpairs})id={id(self)}>"

def _sprite__repr_pretty_(self, p, cycle):
#     p.text('<')
    root = ':'.join((
        self._ptolemaic_class__.__name__,
        str(id(self)),
        ))
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
#     p.text('>')

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


def collect_fields_mro(bases: iter, hints: dict, defaults: dict, /):
    try:
        base = next(bases)
    except StopIteration:
        return
    anno = (dct := base.__dict__).get('__annotations__', {})
    collect_fields_mro(bases, hints, defaults)
    if isinstance(base, Sprite):
        defaults.update(base.Concrete._field_defaults)
    hints.update(anno)


def get_fields(ACls, /):
    collect_fields_mro(iter(ACls.__mro__[1:]), hints := {}, defaults := {})
    hints.update((dct := ACls.__dict__).get('__annotations__', {}))
    for key in hints:
        if key in dct:
            defaults[key] = dct[key]
            delattr(ACls, key)
    if any(hasattr(ACls, key) for key in hints):
        raise TypeError("Field clashes detected!")
    return hints, defaults


class Sprite(_Essence):

    def get_concrete_class(cls, /):
        hints, defaults = get_fields(cls)
        name = f"{cls}_NamedTuple"
        ConcreteBase = _namedtuple(name, hints, defaults=defaults.values())
        signature = _Signature(_Parameter(
            key, 1, default=defaults.get(key, _empty), annotation=hints[key]
            ) for key in hints)
        namespace = dict(
            _basecls=cls,
            __signature__=signature,
            ) | SPRITENAMESPACE
        out = type(cls).create_class_object(
            f"Concrete_{cls.__name__}",
            (cls, ConcreteBase),
            namespace,
            )
        out.__class_pre_init__(out.__name__, out.__bases__, {})
        out.freezeattr.toggle(True)
        return out

    def __class_deep_init__(cls, /):
        super().__class_deep_init__()
        _Dat.register(cls)
        cls._instancesoftcaches = {}
        cls._instanceweakcaches = {}
        Concrete = cls.Concrete = cls.get_concrete_class()
        cls.__callmeth__ = Concrete.__new__.__get__(Concrete)
        cls.__signature__ = Concrete.__signature__

    @property
    def __call__(cls, /):
        return cls.__callmeth__


###############################################################################
###############################################################################
