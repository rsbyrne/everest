###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import functools as _functools
import inspect as _inspect
import itertools as _itertools
import abc as _abc

from everest import ur as _ur

from .sprite import Kwargs as _Kwargs
from .tekton import Tekton as _Tekton, SmartAttr as _SmartAttr
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

    def __bound_get__(self, instance, name, /):
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


class Prop(Cacher):

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
            return instance._organs
        except AttributeError:
            organs = _ur.DatDict(
                organ.__bound_get__(instance, nm)
                for nm, organ in self.items()
                )
            with instance.mutable:
                instance._organs = organs
            return organs


class Organ(_SmartAttr):

    __params__ = ('ligatures',)
    __defaults__ = (_ur.DatDict(),)

    MERGETYPE = Organs

    # @property
    # def __mroclass__(self, /):
    #     return self.hint

    @classmethod
    def get_cachedname(cls, name, /):
        return f"_cached_{name}"

    @staticmethod
    def process_hint(hint, /):
        if not isinstance(hint, (Armature, str)):
            raise TypeError(type(hint))
        return hint

    @staticmethod
    def process_ligatures(ligatures, /):
        return _ur.DatDict(ligatures)

    def _yield_arguments(self, instance, typ, /):
        ligatures = self.ligatures
        for nm, pm in typ.__signature__.parameters.items():
            try:
                altnm = ligatures[nm]
            except KeyError:
                try:
                    val = getattr(instance, nm)
                except AttributeError:
                    val = pm.default
                    if val is _pempty:
                        raise RuntimeError(f"Organ missing argument: {nm}")
            else:
                val = getattr(instance, altnm)
            yield nm, val

    def make_organ(self, instance, name, /):
        typ = self.hint
        if isinstance(typ, str):
            typ = getattr(type(instance), typ)
        params = typ.Params(**dict(self._yield_arguments(instance, typ)))
        epi = typ.taphonomy.getattr_epitaph(instance, name)
        return typ.construct(params, _epitaph=epi)

    def __bound_get__(self, instance, name, /):
        cachedname = self.get_cachedname(name)
        try:
            return getattr(instance, cachedname)
        except AttributeError:
            organ = self.make_organ(instance, name)
            with instance.mutable:
                setattr(instance, cachedname, organ)
            return organ


class Armature(_Tekton, _Composite):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield Prop
        yield Comp
        yield Organ

    @classmethod
    def prop(meta, body, arg: _collabc.Callable = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.prop, body, **kwargs)
        altname = meta._smartattr_namemangle(body, arg)
        return meta.Prop(
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

    __req_slots__ = ('_organs',)

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        for nm, sm in _itertools.chain.from_iterable(
                obj.items() for obj in (cls.__props__, cls.__organs__)
                ):
            yield sm.get_cachedname(nm)


###############################################################################
###############################################################################
