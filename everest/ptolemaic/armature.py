###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import functools as _functools
import inspect as _inspect
import itertools as _itertools
import abc as _abc
import weakref as _weakref

from everest import ur as _ur
from everest.utilities import pretty as _pretty

from .sprite import Kwargs as _Kwargs
from .tekton import (
    Tekton as _Tekton, SmartAttr as _SmartAttr, Getter as _Getter
    )
from .composite import Composite as _Composite


_pempty = _inspect._empty


class Cacher(_SmartAttr):

    __params__ = ('func',)
    __defaults__ = tuple(NotImplemented for key in __params__)

    @classmethod
    def get_cachedname(cls, name, /):
        return f"_cached_{name}"

    @staticmethod
    def process_func(func, /):
        if isinstance(func, (str, _collabc.Callable)):
            return func
        raise TypeError(type(func))

    @_abc.abstractmethod
    def _set_cache(self, instance, value, /):
        raise NotImplementedError

    def __bound_get__(self, instance, owner, name, /):
        cachedname = self.get_cachedname(name)
        try:
            return getattr(instance, cachedname)
        except AttributeError:
            func = self.func
            if isinstance(func, str):
                func = getattr(type(instance), func)
            try:
                value = func(instance)
            except Exception as exc:
                raise RuntimeError from exc
            self._set_cache(instance, cachedname, value)
            return value


class Cached(Cacher):

    def _set_cache(self, instance, cachedname, value, /):
        with instance.mutable:
            setattr(instance, cachedname, value)


class Comp(Cacher):

    def _set_cache(self, instance, cachedname, value, /):
        instance.__vardict__[cachedname] = value


class Organs(_Kwargs):

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        try:
            return instance._boundorgans
        except AttributeError:
            boundorgans = BoundOrgans(instance, owner)
            with instance.mutable:
                instance._boundorgans = boundorgans
            return boundorgans


class BoundOrgans(dict):

    __slots__ = ('_instance', '_owner')

    def __init__(self, instance, owner, /):
        self._instance, self._owner = map(_weakref.ref, (instance, owner))

    @property
    def instance(self, /):
        return self._instance()

    @property
    def owner(self, /):
        return self._owner()

    def __getitem__(self, name, /):
        try:
            return super().__getitem__(name)
        except KeyError:
            instance, owner = self.instance, self.owner
            organ = owner.__organs__[name](instance, owner, name)
            super().__setitem__(name, organ)
            return organ

    def __setitem__(self, name, val, /):
        raise AttributeError

    def __delitem__(self, name, val, /):
        raise AttributeError

    def __repr__(self, /):
        return f"{type(self).__qualname__}({super().__repr__()})"

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = type(self).__qualname__
        _pretty.pretty_kwargs(self, p, cycle, root=root)


class Organ(_SmartAttr):

    __params__ = ('ligatures',)
    __defaults__ = (_ur.DatDict(),)

    MERGETYPE = Organs

    @staticmethod
    def process_ligatures(ligatures, /):
        return _ur.DatDict(ligatures)

    def _yield_arguments(self, instance, owner, typ, /):
        ligatures = self.ligatures
        for nm, pm in typ.__signature__.parameters.items():
            try:
                val = ligatures[nm]
            except KeyError:
                try:
                    val = getattr(instance, nm)
                except AttributeError:
                    val = pm.default
                    if val is _pempty:
                        raise RuntimeError(f"Organ missing argument: {nm}")
            else:
                if isinstance(val, _Getter):
                    val = val(instance, owner)
            yield nm, val

    def __call__(self, instance, owner, name, /):
        typ = self.hint
        if isinstance(typ, _Getter):
            typ = typ(instance, owner)
        params = typ.Params(**dict(self._yield_arguments(instance, owner, typ)))
        epi = typ.taphonomy.getattr_epitaph(instance, name)
        return typ.construct(params, _epitaph=epi)

    def __bound_get__(self, instance, owner, name, /):
        return instance.__organs__[name]


class Armature(_Tekton, _Composite):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield Cached
        yield Comp
        yield Organ

    @classmethod
    def cached(meta, body, arg: _collabc.Callable = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.cached, body, **kwargs)
        altname = meta._smartattr_namemangle(body, arg)
        return meta.Cached(
            hint=arg.__annotations__.get('return', NotImplemented),
            note=arg.__doc__,
            func=altname,
            **kwargs,
            )

    @classmethod
    def comp(meta, body, arg: _collabc.Callable = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.comp, body, **kwargs)
        altname = meta._smartattr_namemangle(body, arg)
        return meta.Comp(
            hint=arg.__annotations__.get('return', NotImplemented),
            note=arg.__doc__,
            func=altname,
            **kwargs,
            )

    @classmethod
    def organ(meta, body, arg: 'Armature' = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.organ, body, **kwargs)
        if not isinstance(arg, Armature):
            raise TypeError(
                f"Organ types must be Armatures or greater: {type(arg)}"
                )
        altname = meta._smartattr_namemangle(body, arg)
        return meta.Organ(hint=altname, ligatures=kwargs)


class ArmatureBase(metaclass=Armature):

    __req_slots__ = ('_boundorgans',)

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        for nm, sm in cls.__cacheds__.items():
            yield sm.get_cachedname(nm)


###############################################################################
###############################################################################
