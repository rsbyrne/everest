###############################################################################
''''''
###############################################################################


from collections import abc as _collabc
import functools as _functools
import inspect as _inspect
import itertools as _itertools
import abc as _abc

from everest import ur as _ur

from .sprite import Tuuple as _Tuuple
from .tekton import Tekton as _Tekton, SmartAttr as _SmartAttr
from .composite import Composite as _Composite


_pempty = _inspect._empty


class Cacher(_SmartAttr):

    __params__ = ('func',)
    __defaults__ = tuple(NotImplemented for key in __params__)

    @staticmethod
    def process_func(func, /):
        if isinstance(func, (str, _collabc.Callable)):
            return func
        raise TypeError(type(func))

    @_abc.abstractmethod
    def _cache_val(self, instance, value, /):
        raise NotImplementedError

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        try:
            return getattr(instance, self.cachedname)
        except AttributeError:
            func = self.func
            if isinstance(func, str):
                func = getattr(owner, func)
            try:
                value = func(instance)
            except Exception as exc:
                raise RuntimeError from exc
            self._cache_val(instance, value)
            return value


class Prop(Cacher):

    def _cache_val(self, instance, value, /):
        with instance.mutable:
            setattr(instance, self.cachedname, value)


class Comp(Cacher):

    def _cache_val(self, instance, value, /):
        instance.__vardict__[self.cachedname] = value


class Organs(_Tuuple):

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        try:
            return instance._organs
        except AttributeError:
            organs = tuple(organ.__get__(instance, owner) for organ in self)
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

    def make_organ(self, instance, owner):
        typ = self.hint
        if isinstance(typ, str):
            typ = getattr(owner, typ)
        params = typ.Params(**dict(self._yield_arguments(instance, typ)))
        epi = typ.taphonomy.getattr_epitaph(instance, self.name)
        return typ.construct(params, _epitaph=epi)

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        try:
            return getattr(instance, self.cachedname)
        except AttributeError:
            organ = self.make_organ(instance, owner)
            with instance.mutable:
                setattr(instance, self.cachedname, organ)
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
        nm, altname = meta._smartattr_namemangle(body, arg)
        return meta.Prop(
            name=nm,
            hint=arg.__annotations__.get('return', NotImplemented),
            note=arg.__doc__,
            func=altname,
            **kwargs,
            )

    @classmethod
    def comp(meta, body, arg: _collabc.Callable = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.comp, body, **kwargs)
        nm, altname = meta._smartattr_namemangle(body, arg)
        return meta.Comp(
            name=nm,
            hint=arg.__annotations__.get('return', NotImplemented),
            note=arg.__doc__,
            func=altname,
            **kwargs,
            )

    @classmethod
    def organ(meta, body, arg: 'Armature' = None, /, **kwargs):
        if arg is None:
            return _functools.partial(meta.organ, body, **kwargs)
        nm, altname = meta._smartattr_namemangle(body, arg)
        return meta.Organ(nm, altname, ligatures=kwargs)


class ArmatureBase(metaclass=Armature):

    __req_slots__ = ('_organs',)

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        for smartattr in _itertools.chain(cls.__props__, cls.__organs__):
            yield smartattr.cachedname


###############################################################################
###############################################################################
