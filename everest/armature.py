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
from everest.utilities.switch import Switch as _Switch


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
            yield from getattr(base, '__req_slots__')

    def __new__(
            meta, arg0, /, *args,
            qualname=None, module=None,
            ):
        locprovided = not all(obj is None for obj in (qualname, module))
        if not args:
            if locprovided:
                raise TypeError(
                    "Location must not be provided " 
                    "while creating Concrete subclass."
                    )
            return super().__new__(
                meta,
                f"{arg0.__name__}_Concrete",
                (_ConcreteBase_, arg0),
                dict(
                    Base=arg0,
                    __slots__=arg0.__req_slots__,
                    _clsfreezeattr=_Switch(False),
                    )
                )
        name, bases, ns = arg0, *args
        ns.setdefault('__qualname__', qualname)
        ns.setdefault('__module__', module)
        params = meta._merge_params(bases, ns)
        slots = tuple(sorted(set((*params, *meta._merge_slots(bases, ns)))))
        ns.update(
            __params__=params,
            __slots__=(),
            __req_slots__=slots,
            _clsfreezeattr=_Switch(False),
            )
        return super().__new__(meta, name, (*bases, _ArmatureBase_), ns)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not issubclass(cls, _ConcreteBase_):
            cls.__class_init__()
        cls._clsfreezeattr.toggle(True)

    @property
    def freezeattr(self, /):
        return self._clsfreezeattr

    def __setattr__(cls, name, val, /):
        try:
            check = cls._clsfreezeattr
        except AttributeError:
            pass
        else:
            if check:
                raise TypeError("Cannot alter attribute on Armature.")
        super().__setattr__(name, val)

    def __delattr__(cls, name, /):
        try:
            check = cls._clsfreezeattr
        except AttributeError:
            pass
        else:
            if check:
                raise TypeError("Cannot alter attribute on Armature.")
        super().__delattr__(name)

    @property
    def mutable(cls, /):
        return cls._clsfreezeattr.as_(False)

    @property
    def __call__(cls, /):
        return cls.__class_call__

    @property
    def taphonomy(cls, /):
        return _FOCUS.bureau.taphonomy


@_ur.Dat.register
class _ArmatureBase_(metaclass=_abc.ABCMeta):

    __slots__ = ('__weakref__', '_objfreezeattr', 'params', '_epitaph')

    param_convert = _ur.Dat.convert

    @classmethod
    def __class_init__(cls, /):
        premade = _weakref.WeakValueDictionary()
        cls._premade = premade
        cls.premade = _types.MappingProxyType(premade)
        pms = cls.__params__
        if pms:
            hints, defaults = zip(*pms.values())
        else:
            hints, defaults = (), ()
        Params = _namedtuple(
            f"{cls.__qualname__}_Params", pms, defaults=defaults
            )
        cls.fieldhints = hints
        cls.Params = Params
        cls.__signature__ = _inspect.signature(Params)
        cls.arity = len(pms)
        cls.Concrete = Armature(cls)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.retrieve(cls.Params(
            *map(cls.param_convert, cls.Params(*args, **kwargs))
            ))

    def __class_getitem__(cls, params, /):
        return cls.retrieve(cls.Params(*map(cls.param_convert, params)))

    @classmethod
    def retrieve(cls, params, /):
        premade = cls._premade
        try:
            return premade[params]
        except KeyError:
            Concrete = cls.Concrete
            obj = premade[params] = Concrete.__new__(Concrete)
            object.__setattr__(obj, 'params', params)
            for name, val in params._asdict().items():
                object.__setattr__(obj, name, val)
            object.__setattr__(obj, '_objfreezeattr', _Switch(True))
            with obj.mutable:
                obj.__init__()
            return obj

    @property
    def freezeattr(self, /):
        return self._objfreezeattr

    @property
    def mutable(self, /):
        return self._objfreezeattr.as_(False)

    def __setattr__(self, name, val, /):
        try:
            check = self._objfreezeattr
        except AttributeError:
            pass
        else:
            if check:
                raise TypeError("Cannot alter attribute on Armature.")
        super().__setattr__(name, val)

    def __delattr__(self, name, /):
        try:
            check = self._objfreezeattr
        except AttributeError:
            pass
        else:
            if check:
                raise TypeError("Cannot alter attribute on Armature.")
        super().__delattr__(name)

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


###############################################################################
###############################################################################
