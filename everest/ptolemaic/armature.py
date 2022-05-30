###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from everest import ur as _ur

from .tekton import Tekton as _Tekton, SmartAttr as _SmartAttr
from .composite import Composite as _Composite


class Prop(_SmartAttr):

    __params__ = ('func',)
    __defaults__ = tuple(NotImplemented for key in __params__)

    @staticmethod
    def process_func(func, /):
        return func

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        try:
            return getattr(instance, self.cachedname)
        except AttributeError:
            try:
                value = self.func(instance)
            except Exception as exc:
                raise RuntimeError from exc
            with instance.mutable:
                setattr(instance, self.cachedname, value)
            return value


class Organ(_SmartAttr):

    __params__ = ('ligatures',)
    __defaults__ = (_ur.DatDict(),)

    # @property
    # def __mroclass__(self, /):
    #     return self.hint

    @staticmethod
    def process_hint(hint, /):
        if not isinstance(hint, Armature):
            raise ValueError(hint)
        return hint

    @staticmethod
    def process_ligatures(ligatures, /):
        return _ur.DatDict(ligatures)   

    def __get__(self, instance, owner=None, /):
        if instance is None:
            return self
        try:
            return getattr(instance, self.cachedname)
        except AttributeError:
            typ = self.hint
            bound = typ.__signature__.bind(**self.ligatures)
            bound.apply_defaults()
            params = typ.Params(**bound.arguments)
            epi = typ.taphonomy.getattr_epitaph(instance, self.name)
            out = typ.construct(params, _epitaph=epi)
            with instance.mutable:
                setattr(instance, self.cachedname, out)
            return out

class Comp(_SmartAttr):

    def __set__(self, instance, value, /):
        setattr(instance, self.cachedname, value)


class Armature(_Tekton, _Composite):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield Prop
        yield Comp
        yield Organ

    @classmethod
    def prop(meta, func: _collabc.Callable, /):
        return meta.Prop(name=func.__name__, func=func)

    @classmethod
    def organ(meta, typ: 'Armature' = None, /, **ligatures):
        if typ is None:
            return _functools.partial(**ligatures)
        return meta.Organ(name=typ.__name__, hint=typ, ligatures=ligatures)


class ArmatureBase(metaclass=Armature):

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from super()._yield_concrete_slots()
        for smartattr in cls.__props__.values():
            yield smartattr.cachedname
        for smartattr in cls.__organs__.values():
            yield smartattr.cachedname

#     @classmethod
#     def __class_set_name__(cls, owner, name, /):


#     @classmethod
#     def __class_get__(cls, instance, owner=None, /):
#         if instance is None:
#             return cls
#         try:
#             return 

    # @classmethod
    # def create_organ(cls, name, hint, note, ligatures, /):




###############################################################################
###############################################################################
