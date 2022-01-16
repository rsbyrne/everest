###############################################################################
''''''
###############################################################################


from collections import namedtuple as _namedtuple
import functools as _functools
from inspect import Signature as _Signature, Parameter as _Parameter, _empty
import weakref as _weakref

from everest.utilities import (
    caching as _caching,
    )
from everest.ur import Dat as _Dat

from everest.ptolemaic.essence import Essence as _Essence


def collect_fields_mro(bases: iter, hints: dict, defaults: dict, seen: set, /):
    try:
        base = next(bases)
    except StopIteration:
        return
    anno = (dct := base.__dict__).get('__annotations__', {})
    collect_fields_mro(bases, hints, defaults, seen | set(anno))
    if isinstance(base, Sprite):
        defaults.update(base.Concrete._field_defaults)
    hints.update({key: anno[key] for key in anno if key not in seen})


def get_fields(ACls, /):
    anno = (dct := ACls.__dict__).get('__annotations__', {})
    bases = iter(ACls.__mro__[1:])
    collect_fields_mro(bases, hints := {}, defaults := {}, set(anno))
    hints.update(anno)
    for key in hints:
        if key in dct:
            defaults[key] = dct[key]
            delattr(ACls, key)
    if any(hasattr(ACls, key) for key in hints):
        raise TypeError("Field clashes detected!")
    return hints, defaults


class Sprite(_Essence):

    def get_concrete_namespace(cls, /):
        return dict(
            _basecls=cls,
            )# | SPRITENAMESPACE

    def get_concrete_base(cls, /):
        hints, defaults = get_fields(cls)
        name = f"{cls}_NamedTuple"
        ConcreteBase = _namedtuple(name, hints, defaults=defaults.values())
        ConcreteBase.__signature__ = _Signature(_Parameter(
            key, 1, default=defaults.get(key, _empty), annotation=hints[key]
            ) for key in hints)
        return ConcreteBase

    def get_concrete_class(cls, /):
        out = type(cls).create_class_object(
            f"Concrete_{cls.__name__}",
            (cls, cls.get_concrete_base()),
            cls.get_concrete_namespace(),
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
        cls.__callmeth__ = _functools.partial(Concrete.__new__, Concrete)
        cls.__signature__ = Concrete.__signature__

    @property
    def __call__(cls, /):
        return cls.__callmeth__


class SpriteBase(metaclass=Sprite):

    def get_epitaph(self, /):
        ptolcls = self._ptolemaic_class__
        return ptolcls.taphonomy.callsig_epitaph(
            ptolcls, *self.params.values()
            )

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.get_epitaph()

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    @property
    def softcache(self, /):
        num = id(self)
        try:
            return self._instancesoftcaches[num]
        except KeyError:
            out = self._instancesoftcaches[num] = {}
            return out

    @property
    def weakcache(self, /):
        num = id(self)
        try:
            return self._instanceweakcaches[num]
        except KeyError:
            out = self._instanceweakcaches[num] = _weakref.WeakValueDictionary()
            return out

    @property
    def _ptolemaic_class__(self, /):
        return self._basecls

    def __del__(self, /):
        num = id(self)
        for cache in (self._instancesoftcaches, self._instanceweakcaches):
            try:
                del cache[num]
            except KeyError:
                pass

    def __repr__(self, /):
        valpairs = ', '.join(map('='.join, zip(
            (params := self.params),
            map(repr, params.values()),
            )))
        return f"<{self._ptolemaic_class__}({valpairs})id={id(self)}>"

    def _repr_pretty_(self, p, cycle):
    #     p.text('<')
        root = ':'.join((
            self._ptolemaic_class__.__name__,
            str(id(self)),
            ))
        if cycle:
            p.text(root + '{...}')
        elif not (kwargs := {
                key: getattr(self, key) for key in self._fields
                }):
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
    def __getitem__(self, /):
        return super().__getitem__


###############################################################################
###############################################################################
