###############################################################################
''''''
###############################################################################


import functools as _functools
import collections as _collections
import operator as _operator
import weakref as _weakref
import types as _types
import inspect as _inspect

from everest.utilities import (
    caching as _caching, reseed as _reseed, pretty as _pretty
    )
from everest.ur import Dat as _Dat
from everest.incision import IncisionProtocol as _IncisionProtocol

from everest.ptolemaic.essence import Essence as _Essence
from everest.ptolemaic.ousia import Ousia as _Ousia
from everest.ptolemaic.diict import Kwargs as _Kwargs
from everest.ptolemaic import exceptions as _exceptions

from .tekton import Tekton as _Tekton
from .brace import Brace as _Brace
from .chora import Chora as _Chora, Degenerate as _Degenerate
from .sig import (Params as _Params, Param as _Param)


@_Dat.register
class Eidos(_Tekton, _Ousia):

    @property
    def __call__(cls, /):
        return cls.__class_call__

    @property
    def __construct__(cls, /):
        return cls

#     @property
#     @_caching.soft_cache()
#     def _classchoras(cls, /):
#         return _types.MappingProxyType(cls._get_classchoras())

#     @property
#     @_caching.soft_cache()
#     def _classconstructors(cls, /):
#         return _types.MappingProxyType(cls._get_classconstructors())

#     @property
#     @_caching.soft_cache()
#     def __instance_incision_manager__(cls, /):
#         return _Brace[_Kwargs(cls._classchoras)]


class EidosBase(metaclass=Eidos):

    _req_slots__ = ('params',)

    CACHE = False

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        cls.premade = _weakref.WeakValueDictionary()
        if cls._var_slots__:
            raise TypeError(
                f"Types metatype {type(cls)} cannot have var slots."
                )

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        params = _Params(cls.parameterise(cache := {}, *args, **kwargs))
        try:
            return cls.premade[params]
        except KeyError:            
            cls.check_params(params)
            obj = cls.premade[params] = cls.instantiate(params)
            obj.softcache.update(cache)
            return obj

    @classmethod
    def instantiate(cls, params, /):
        obj = object.__new__(cls.Concrete)
        obj.params = params
        obj.__init__()
        obj.freezeattr.toggle(True)
        return obj

    @classmethod
    def pre_create_concrete(cls, /):
        name, bases, namespace = super().pre_create_concrete()
        namespace.update({key: _Param(key) for key in cls.fields})
        return name, bases, namespace

    @classmethod
    def paramexc(cls, /, *args, message=None, **kwargs):
        return _exceptions.ParameterisationException(
            (args, kwargs), cls, message
            )

    @classmethod
    def parameterise(cls, cache, /, *args, **kwargs):
        bound = cls.__signature__.bind(*args, **kwargs)
        bound.apply_defaults()
        return bound

    @classmethod
    def check_params(cls, params: _Params, /):
        pass

    def remake(self, /, **kwargs):
        ptolcls = self._ptolemaic_class__
        bound = ptolcls.__signature__.bind_partial()
        bound.arguments.update(self.params)
        bound.arguments.update(kwargs)
        return ptolcls(*bound.args, **bound.kwargs)

    ### Serialisation

    def get_epitaph(self, /):
        return self.taphonomy.custom_epitaph(
            "$a.instantiate($b)",
            a=self._ptolemaic_class__, b=self.params,
            )

    @property
    @_caching.soft_cache()
    def epitaph(self, /):
        return self.get_epitaph()

    ### Representations:

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def _root_repr(self, /):
        ptolcls = self._ptolemaic_class__
        objs = (
            type(ptolcls).__qualname__, ptolcls.__qualname__, self.hashID
            )
        return ':'.join(map(str, objs))

    def _content_repr(self, /):
        return ', '.join(
            f"{key}={repr(val)}" for key, val in self.params.items()
            )

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self._ptolemaic_class__.__name__
        _pretty.pretty_kwargs(self.params, p, cycle, root=root)

    def __hash__(self, /):
        return self.hashint


###############################################################################
###############################################################################


#     ### Incision protocol

#     class Oid(metaclass=_Essence):

#         @classmethod
#         def __class_call__(cls, chora):
#             try:
#                 meth = cls.owner._classconstructors[chora.active]
#             except KeyError:
#                 return super().__class_call__(chora)
#             else:
#                 return meth(chora)

#         @property
#         def active(self, /):
#             return self.chora.active

#         @property
#         def choras(self, /):
#             return self.chora.choras

#         @property
#         @_caching.soft_cache()
#         def sig(self, /):
#             return self.subject.sig.__incise_slyce__(self.choras[0])

#         def __incise_retrieve__(self, incisor, /):
#             print(incisor)
#             itinc = iter(incisor)
#             out = self.subject._instantiate_from_incisor(itinc)
#             for inc in itinc:
#                 out = _IncisionProtocol.RETRIEVE(out)(inc)
#             return out

#     @classmethod
#     def _instantiate_from_incisor(cls, incisor, /):
#         return cls.instantiate(
#             cls.sig.__incise_retrieve__(next(iter(incisor)))
#             )

#     @classmethod
#     def _get_classchoras(cls, /):
#         return dict()

#     @classmethod
#     def _get_classconstructors(cls, /):
#         return {}
#         # return {
#         #     (False, *tuple(True for _ in cls._classchoras)): (
#         #         cls._instantiate_from_incisor
#         #         )
#         #     }

#     @classmethod
#     def _make_classspace(cls, /):
#         return cls.Oid(_Brace[_Kwargs(
#             fields=cls.sig.__incision_manager__,
#             **cls._classchoras,
#             )])

#     @property
#     def __incision_manager__(self, /):
#         return self.__instance_incision_manager__