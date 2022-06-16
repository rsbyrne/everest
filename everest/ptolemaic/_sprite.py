###############################################################################
''''''
###############################################################################


import inspect as _inspect
import collections as _collections

from everest.utilities import pretty as _pretty

from .ousia import Ousia as _Ousia
from . import ptolemaic as _ptolemaic


_pempty = _inspect._empty


class Sprite(_Ousia):

    @classmethod
    def process_bodyanno(meta, body, name, hint, val, /):
        body['__params__'][name] = (hint, val)
        return None, None

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield ('__params__', dict, _ptolemaic.PtolDict)


class _SpriteBase_(metaclass=Sprite):

    __slots__ = ('_params',)

    @classmethod
    def classbody_finalise(meta, body, /):
        super().classbody_finalise(body)
        body['__req_slots__'].extend(body['__params__'])

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        pms = cls.__params__
        hints, defaults = cls.fieldhints, cls.fieldefaults = tuple(
            _ptolemaic.PtolDict(zip(pms, vals))
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

    @property
    def params(self, /):
        return self._params

    @params.setter
    def params(self, value, /):
        params = self._params = self.Params(*value)
        for name, param in params._asdict().items():
            setattr(self, name, param)

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        return super().parameterise(**cls.Params(*args, **kwargs)._asdict())

    def make_epitaph(self, /):
        cls = self.__ptolemaic_class__
        return cls.taphonomy.getitem_epitaph(cls, tuple(self.params))

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}"
            for key, val in self.params._asdict().items()
            )

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_tuple(self.params, p, cycle, root=root)


###############################################################################
###############################################################################
