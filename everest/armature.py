###############################################################################
''''''
###############################################################################


import abc as _abc
from collections import namedtuple as _namedtuple, abc as _collabc
import weakref as _weakref
import types as _types
import inspect as _inspect
import itertools as _itertools

from everest import ur as _ur
from everest.utilities import pretty as _pretty
from everest.switch import Switch as _Switch
# from everest.utilities.switch import Switch as _Switch


_pkind = _inspect._ParameterKind


class _ConcreteBase_(metaclass=_abc.ABCMeta):

    __slots__ = ()

    @classmethod
    def __mro_entries__(cls, bases: tuple, /):
        return (cls.Base,)


@_ur.Dat.register
class Armature(_abc.ABCMeta):

    @classmethod
    def _merge_params(meta, bases, ns, /):
        nsparams = ns.pop('__fields__', {})
        try:
            annos = ns.pop('__annotations__')
        except KeyError:
            pass
        else:
            for name, hint in annos.items():
                nsparams[name] = (hint, ns.pop(name, NotImplemented))
        baseparams = tuple(getattr(base, '__fields__', {}) for base in bases)
        return _ur.DatDict(_itertools.chain.from_iterable(
            params.items() for params in reversed((nsparams, *baseparams))
            ))

    @classmethod
    def _get_merged_slots(meta, bases, ns, params, /):
        out = {}
        baseslots = (getattr(base, '__req_slots__', {}) for base in (
            *reversed(bases),
            *reversed(meta.BaseTyp.__bases__),
            meta.BaseTyp,
            ))
        for slots in (*baseslots, ns.pop('__slots__', {})):
            if not isinstance(slots, _collabc.Mapping):
                slots = zip(slots, _itertools.repeat(None))
            out.update(slots)
        out.update((key, typ) for key, (typ, _) in params.items())
        return _ur.DatDict(out)

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
        slots = meta._get_merged_slots(bases, ns, params)
        ns.update(
            __fields__=params,
            __slots__=(),
            __req_slots__=slots,
            _clsmutable=_Switch(True),
            )
        return super().__new__(meta, name, (*bases, meta.BaseTyp), ns)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if issubclass(cls, _ConcreteBase_):
            cls.__ptolemaic_class__ = cls.Base
        else:
            cls.__ptolemaic_class__ = cls
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
                val = cls.param_convert(val)
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
    def param_convert(cls, /):
        return _ur.Dat.convert


@_ur.Dat.register
class _ArmatureBase_(metaclass=_abc.ABCMeta):

    __req_slots__ = ('__weakref__', '_mutable', 'params')
    __slots__ = ()

    @classmethod
    def _get_signature(cls, /):
        return _inspect.Signature(
            _inspect.Parameter(
                name, _pkind['POSITIONAL_OR_KEYWORD'],
                default=default, annotation=hint
                )
            for name, (hint, default) in cls.__fields__.items()
            )

    @classmethod
    def __class_init__(cls, /):
        cls._premade = _weakref.WeakValueDictionary()
        cls.__signature__ = cls._get_signature()
        cls.arity = len(cls.__fields__)
        cls.Concrete = type(cls)(cls)

    def __initialise__(self, /):
        self.__init__()
        self.mutable = False

    @classmethod
    def _instantiate_(cls, params: tuple, /):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        mutable = _Switch(True)
        object.__setattr__(obj, '_mutable', mutable)
        object.__setattr__(obj, 'params', params)
        for name, val in zip(cls.__fields__, params):
            object.__setattr__(obj, name, val)
        return obj

    @classmethod
    def __instantiate__(cls, params: tuple, /):
        return cls._instantiate_(tuple(map(cls.param_convert, params)))

    @classmethod
    def _construct_(cls, params: tuple, /):
        obj = cls._instantiate_(params)
        obj.__initialise__()
        return obj

    @classmethod
    def __construct__(cls, params: tuple, /):
        return cls._construct_(tuple(map(cls.param_convert, params)))

    @classmethod
    def _retrieve_(cls, params: tuple, /):
        premade = cls._premade
        try:
            return premade[params]
        except KeyError:
            obj = premade[params] = cls._construct_(params)
            return obj

    @classmethod
    def __retrieve__(cls, params: tuple, /):
        return cls._retrieve_(tuple(map(cls.param_convert, params)))

    @classmethod
    def __parameterise__(cls, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return _types.SimpleNamespace(**bound.arguments)

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.__retrieve__(tuple(
            cls.__parameterise__(*args, **kwargs)
            .__dict__.values()
            ))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, arg, /):
        return cls.__retrieve__(arg)

    @property
    def mutable(self, /):
        return self._mutable

    @mutable.setter
    def mutable(self, value, /):
        self.mutable.toggle(value)

    def __setattr__(self, name, val, /):
        if self._mutable:
            if not name.startswith('_'):
                val = type(self).param_convert(val)
            super().__setattr__(name, val)
        else:
            raise TypeError("Cannot alter attribute when immutable.")

    def __delattr__(self, name, /):
        if self._mutable:
            super().__delattr__(name)
        else:
            raise TypeError("Cannot alter attribute when immutable.")

    def __repr__(self, /):
        return f"<{self.Base.__qualname__}, id={id(self)}>"

    def __str__(self, /):
        return f"{self.Base.__qualname__}({repr(self.params)[1:-1]})"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.Base.__qualname__
        _pretty.pretty_tuple(self.params, p, cycle, root=root)

    def __hash__(self, /):
        return hash((self.Base, self.params))

    def __reduce__(self, /):
        return self.Base.__class_getitem__, (self.params,)


Armature.BaseTyp = _ArmatureBase_


###############################################################################
###############################################################################
