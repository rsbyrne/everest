###############################################################################
''''''
###############################################################################


from collections import namedtuple as _namedtuple, deque as _deque
import functools as _functools
from inspect import Signature as _Signature, Parameter as _Parameter, _empty
import weakref as _weakref

from everest.utilities import (
    caching as _caching, FrozenMap as _FrozenMap
    )
from everest.ur import Dat as _Dat

from everest.ptolemaic.essence import Essence as _Essence


def collect_fields_mro(
        bases: iter, hints: dict, defaults: dict, inorder: _deque, /
        ):
    try:
        base = next(bases)
    except StopIteration:
        return
    anno = (dct := base.__dict__).get('__annotations__', {})
    collect_fields_mro(bases, hints, defaults, inorder)
    if isinstance(base, Sprite):
        defaults.update(base.Concrete._field_defaults)
    for key, val in anno.items():
        if key in inorder:
            deq = hints[key]
        else:
            deq = hints[key] = _deque()
            inorder.append(key)
        deq.append(val)


def get_fields(ACls, /):
    anno = (dct := ACls.__dict__).get('__annotations__', {})
    hints = {key: _deque((val,)) for key, val in anno.items()}
    bases = iter(ACls.__mro__[1:])
    collect_fields_mro(bases, hints, defaults := {}, inorder := _deque())
    for key in anno:
        if key not in inorder:
            inorder.append(key)
        if key in dct:
            defaults[key] = dct[key]
            delattr(ACls, key)
    out = {}
    for key in inorder:
        try:
            out[key] = hints[key][-1]
        except IndexError:
            out[key] = _empty
    if any(hasattr(ACls, key) for key in out):
        raise TypeError("Field clashes detected!")
    return out, defaults


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
        base = cls.get_concrete_base()
        out = type(cls).create_class_object(
            f"Concrete_{cls.__name__}",
            (cls, base),
            cls.get_concrete_namespace(),
            )
        out.__signature__ = base.__signature__
        out.__class_pre_init__(out.__name__, out.__bases__, {})
        out.freezeattr.toggle(True)
        return out

    def __class_deep_init__(cls, /):
        super().__class_deep_init__()
        _Dat.register(cls)
        cls._instancesoftcaches = {}
        cls._instanceweakcaches = {}
        Concrete = cls.Concrete = cls.get_concrete_class()
#         cls.create_object = _functools.partial(Concrete.__new__, Concrete)
#         cls.__callmeth__ = 
#         cls.__callmeth__ = Concrete.__new__.__get__(Concrete)
        cls.__signature__ = Concrete.__signature__

#     def __call__(cls, /):
#         return cls.__callmeth__


class SpriteBase(metaclass=Sprite):

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        conc = cls.Concrete
        obj = conc.__new__(conc, *args, **kwargs)
        obj.__init__()
        return obj

    def __init__(self, /):
        pass

    @property
    @_caching.soft_cache()
    def params(self, /):
        return _FrozenMap({key: getattr(self, key) for key in self._fields})

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
            out = self._instanceweakcaches[num] = \
                _weakref.WeakValueDictionary()
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

    def __hash__(self, /):
        return self.hashint

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        return hash(self) < hash(other)

    def __gt__(self, other, /):
        return hash(self) < hash(other)


###############################################################################
###############################################################################
