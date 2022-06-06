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

from .content import Kwargs as _Kwargs
from .tekton import Tekton as _Tekton
from .smartattr import (
    SmartAttr as _SmartAttr, Getter as _Getter, OwnerGet as _OwnerGet
    )
from .ousia import Ousia as _Ousia


_pempty = _inspect._empty


class Cacher(_SmartAttr):

    callobj: _collabc.Callable

    @classmethod
    def get_cachedname(cls, name, /):
        return f"_cached_{name}"

    @staticmethod
    def process_callobj(arg, /):
        if isinstance(arg, _collabc.Callable):
            return arg
        if isinstance(arg, str):
            return _OwnerGet(arg)
        raise TypeError(type(arg))

    @_abc.abstractmethod
    def _set_cache(self, instance, value, /):
        raise NotImplementedError

    def __bound_get__(self, instance, owner, name, /):
        if instance is None:
            return self.callobj
        cachedname = self.get_cachedname(name)
        try:
            return getattr(instance, cachedname)
        except AttributeError:
            callobj = self.callobj
            if isinstance(callobj, _Getter):
                callobj = callobj(instance, owner)
            try:
                value = callobj(instance)
            except Exception as exc:
                raise RuntimeError from exc
            self._set_cache(instance, cachedname, value)
            return value


class Cached(Cacher):

    def _set_cache(self, instance, cachedname, value, /):
        with instance.mutable:
            setattr(instance, cachedname, value)


class Ligated(_SmartAttr):

    ligatures: _collabc.Mapping = _ur.DatDict()

    @staticmethod
    def process_ligatures(arg, /):
        return _ur.DatDict(arg)


class Comp(Cacher, Ligated):

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


class Organ(Ligated):

    MERGETYPE = Organs

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
        params = typ.Params(**dict(
            self._yield_arguments(instance, owner, typ)
            ))
        epi = typ.taphonomy.getattr_epitaph(instance, name)
        return typ.construct(params, _epitaph=epi)

    def __bound_get__(self, instance, owner, name, /):
        return instance.__organs__[name]


class Schema(_Tekton, _Ousia):

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
            callobj=altname,
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
            callobj=altname,
            **kwargs,
            )

    @classmethod
    def organ(meta, body, arg: 'Schema' = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.organ, body, **kwargs)
        if not isinstance(arg, Schema):
            raise TypeError(
                f"Organ types must be Schemas or greater: {type(arg)}"
                )
        altname = meta._smartattr_namemangle(body, arg)
        return meta.Organ(hint=altname, ligatures=kwargs)


class SchemaBase(metaclass=Schema):

    __slots__ = ('params', '_boundorgans',)

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        for nm, sm in cls.__cacheds__.items():
            yield sm.get_cachedname(nm)

    def set_params(self, params, /):
        self.params = params

    def remake(self, /, **kwargs):
        return self.__ptolemaic_class__.retrieve(
            tuple({**self.params._asdict(), **kwargs}.values())
            )

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}"
            for key, val in self.params._asdict().items()
            )

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def _repr_pretty_(self, p, cycle, root=None):
        bound = self.__signature__.bind_partial()
        bound.arguments.update(self.params._asdict())
        if root is None:
            root = self.rootrepr
        _pretty.pretty_argskwargs(
            (bound.args, bound.kwargs), p, cycle, root=root
            )

    def make_epitaph(self, /):
        cls = self.__ptolemaic_class__
        return cls.taphonomy.getitem_epitaph(cls, tuple(self.params))


###############################################################################
###############################################################################
