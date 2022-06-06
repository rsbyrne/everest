###############################################################################
''''''
###############################################################################


import inspect as _inspect
import collections as _collections

from everest.utilities import pretty as _pretty
from everest import ur as _ur

from .ousia import Ousia as _Ousia


_pempty = _inspect._empty


class Sprite(_Ousia):

    @classmethod
    def pre_create_class(meta, name, bases, ns, /):
        name, bases, ns = super().pre_create_class(name, bases, ns)
        params = dict(ns.pop('__params__'))
        annos = ns.pop('__annotations__')
        params.update(
            (nm, (hint, val))
            for nm, (hint, val) in annos.items()
            )
        ns['__params__'] = _ur.DatDict(params)
        return name, bases, ns


class SpriteBase(metaclass=Sprite):

    MERGENAMES = (
        ('__params__', dict),
        )

    __slots__ = ('params',)

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        yield from cls.Params._fields

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        pms = cls.__params__
        hints, defaults = cls.fieldhints, cls.fieldefaults = tuple(
            _ur.DatDict(zip(pms, vals))
            for vals in (zip(*pms.values()) if pms else ((), ()))
            )
        Params = _collections.namedtuple(
            f"{cls.__qualname__}_Params", pms, defaults=defaults.values()
            )
        cls.Params = Params
        cls.__signature__ = _inspect.signature(Params)
        cls.arity = len(pms)

    @classmethod
    def _get_signature(cls, /):
        return _inspect.signature(cls.Params)

    def set_params(self, params, /):
        params = self.params = self.Params(*params)
        for name, param in params._asdict().items():
            setattr(self, name, param)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return super().parameterise(**cls.Params(*args, **kwargs)._asdict())

    def make_epitaph(self, /):
        cls = self.__ptolemaic_class__
        return cls.taphonomy.getitem_epitaph(cls, tuple(self.params))

    def __str__(self, /):
        return f"{self.__ptolemaic_class__.__qualname__}({repr(self.params)})"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_tuple(self.params, p, cycle, root=root)


###############################################################################
###############################################################################
