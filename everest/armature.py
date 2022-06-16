###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import namedtuple as _namedtuple
import weakref as _weakref
import types as _types
import inspect as _inspect
import itertools as _itertools

from everest import ur as _ur
from everest.utilities import pretty as _pretty
from everest.switch import Switch as _Switch
# from everest.utilities.switch import Switch as _Switch


class _ConcreteBase_(metaclass=_abc.ABCMeta):

    __slots__ = ()

    @classmethod
    def __mro_entries__(cls, bases: tuple, /):
        return (cls.Base,)


@_ur.Dat.register
class Armature(_abc.ABCMeta):

    @classmethod
    def _merge_params(meta, bases, ns, /):
        nsparams = ns.pop('__params__', {})
        try:
            annos = ns.pop('__annotations__')
        except KeyError:
            pass
        else:
            for name, hint in annos.items():
                nsparams[name] = (hint, ns.pop(name, NotImplemented))
        baseparams = tuple(getattr(base, '__params__', {}) for base in bases)
        return _ur.DatDict(_itertools.chain.from_iterable(
            params.items() for params in reversed((nsparams, *baseparams))
            ))

    @classmethod
    def _merge_slots(meta, bases, ns, /):
        yield from ns.pop('__slots__', ())
        for base in bases:
            yield from getattr(base, '__req_slots__', ())

    def __new__(meta, arg0, /, *args):
        if not args:
            return super().__new__(
                meta,
                f"{arg0.__name__}_Concrete",
                (_ConcreteBase_, arg0),
                dict(
                    Base=arg0,
                    __slots__=arg0.__req_slots__,
                    _clsmutable=_Switch(True),
                    )
                )
        name, bases, ns = arg0, *args
        if not _ConcreteBase_ in bases:
            if not all(nm in ns for nm in ('__qualname__', '__module__')):
                raise TypeError(
                    "Armature-derived classes must be top-level classes."
                    )
        params = meta._merge_params(bases, ns)
        slots = tuple(sorted(set((*params, *meta._merge_slots(bases, ns)))))
        ns.update(
            __params__=params,
            __slots__=(),
            __req_slots__=slots,
            _clsmutable=_Switch(True),
            )
        return super().__new__(meta, name, (*bases, meta.BaseTyp), ns)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not issubclass(cls, _ConcreteBase_):
            cls.__class_init__()
        cls._clsmutable.toggle(True)

    @property
    def mutable(cls, /):
        return cls.__dict__['_clsmutable']

    @mutable.setter
    def mutable(cls, val, /):
        cls.mutable.toggle(val)

    def __setattr__(cls, name, val, /):
        if cls.__dict__['_clsmutable']:
            if not name.startswith('_'):
                val = cls.convert(val)
            super().__setattr__(name, val)
        else:
            raise TypeError("Cannot alter attribute when immutable.")

    def __delattr__(cls, name, /):
        if cls.__dict__['_clsmutable']:
            super().__delattr__(name)
        else:
            raise TypeError("Cannot alter attribute when immutable.")

    @property
    def __call__(cls, /):
        return cls.__class_call__

    @property
    def taphonomy(cls, /):
        return _FOCUS.bureau.taphonomy

    def convert(cls, obj, /):
        return _ur.Dat.convert(obj)


@_ur.Dat.register
class _ArmatureBase_(metaclass=_abc.ABCMeta):

    __slots__ = ('__weakref__', '_mutable', 'params', '_epitaph')

    @classmethod
    def __class_init__(cls, /):
        premade = _weakref.WeakValueDictionary()
        cls._premade = premade
        pms = cls.__params__
        if pms:
            hints, defaults = zip(*pms.values())
        else:
            hints, defaults = (), ()
        Params = _namedtuple(
            f"{cls.__qualname__}_Params", pms, defaults=defaults
            )
        cls._Params = Params
        cls.fieldhints = hints
        cls.__signature__ = _inspect.signature(Params)
        cls.arity = len(pms)
        cls.Concrete = Armature(cls)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls._retrieve_(cls._Params(
            *map(cls.convert, cls._Params(*args, **kwargs))
            ))

    def __class_getitem__(cls, params, /):
        return cls._retrieve_(cls._Params(*map(cls.convert, params)))

    @classmethod
    def _retrieve_(cls, params, /):
        premade = cls._premade
        try:
            return premade[params]
        except KeyError:
            Concrete = cls.Concrete
            obj = premade[params] = Concrete.__new__(Concrete)
            mutable = _Switch(True)
            object.__setattr__(obj, '_mutable', mutable)
            object.__setattr__(obj, 'params', params)
            for name, val in params._asdict().items():
                object.__setattr__(obj, name, val)
            obj.__init__()
            mutable.toggle(False)
            return obj

    @property
    def mutable(self, /):
        return self._mutable

    @mutable.setter
    def mutable(self, value, /):
        self.mutable.toggle(value)

    def __setattr__(self, name, val, /):
        if object.__getattribute__(self, '_mutable'):
            if not name.startswith('_'):
                val = type(self).convert(val)
            super().__setattr__(name, val)
        else:
            raise TypeError("Cannot alter attribute when immutable.")

    def __delattr__(self, name, /):
        if object.__getattribute__(self, '_mutable'):
            super().__delattr__(name)
        else:
            raise TypeError("Cannot alter attribute when immutable.")

    def __repr__(self, /):
        return f"<{self.Base.__qualname__}, id={id(self)}>"

    def __str__(self, /):
        return f"{self.Base.__qualname__}({repr(tuple(self.params))[1:-1]})"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.Base.__qualname__
        _pretty.pretty_tuple(self.params, p, cycle, root=root)

    def __hash__(self, /):
        return hash((self.Base, self.params))

    def __reduce__(self, /):
        return self.Base.__class_getitem__, (tuple(self.params),)


Armature.BaseTyp = _ArmatureBase_


###############################################################################
###############################################################################
