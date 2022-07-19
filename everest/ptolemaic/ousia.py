###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
from collections import abc as _collabc

from everest.utilities import reseed as _reseed
from everest.bureau import FOCUS as _FOCUS
from everest.switch import Switch as _Switch
from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .urgon import Urgon as _Urgon


class ConcreteBase:

    __slots__ = ()

    for methname in (
            '__class_call__',
            'create_concrete', 'pre_create_concrete',
            ):
        exec('\n'.join((
            f"@classmethod",
            f"def {methname}(cls, /, *_, **__):",
            f"    raise AttributeError(",
            f"        '{methname} not supported on Concrete subclasses.'",
            f"        )",
            )))
    del methname


@_ptolemaic.Kind.register
class Ousia(_Urgon):

    @property
    def Concrete(cls, /):
        cls = cls.__ptolemaic_class__
        try:
            return cls.__dict__['_Concrete']
        except KeyError:
            with cls.mutable:
                out = cls._Concrete = _abc.ABCMeta.__new__(
                    type(cls), *cls.pre_create_concrete()
                    )
                out.mutable = False
            return out

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield '__req_slots__', dict, dict

    @classmethod
    def handle_slots(meta, body, slots, /):
        if not isinstance(slots, _collabc.Mapping):
            slots = zip(slots, _itertools.repeat(None))
        body['__req_slots__'].update(slots)


@_ptolemaic.Case.register
class _OusiaBase_(metaclass=Ousia):

    __slots__ = (
        '__weakref__',
        'params', '_mutable', '_pyhash', '_sessioncacheref',
        '_innerobjs', '__corpus__', '__relname__', '_instancesignature',
        )

    @classmethod
    def __class_contains__(cls, arg, /):
        return isinstance(arg, cls)

    @classmethod
    def __class_includes__(cls, arg, /):
        return issubclass(arg, cls)

    @property
    def __signature__(self, /):
        try:
            return object.__getattribute__(self, '_instancesignature')
        except AttributeError:
            try:
                meth = self.__get_signature__
            except AttributeError:
                raise TypeError(self.__ptolemaic_class__)
            sig = meth()
            object.__setattr__(self, '_instancesignature', sig)
            return sig

    ### Descriptor behaviours for class and instance:

    def register_innerobj(self, name, obj, /):
        _ptolemaic.configure_as_innerobj(obj, self, name)
        if self.mutable:
            try:
                innerobjs = object.__getattribute__(self, '_innerobjs')
            except AttributeError:
                innerobjs = {}
                object.__setattr__(self, '_innerobjs', innerobjs)
            innerobjs[name] = obj
        else:
            try:
                meth = obj.__initialise__
            except AttributeError:
                pass
            else:
                meth()

    ## Configuring the class:

    @classmethod
    def _yield_slots(cls, /):
        yield from cls.__req_slots__.items()

    @classmethod
    def pre_create_concrete(cls, /):
        cls = cls.__ptolemaic_class__
        return (
            f"{cls.__name__}_Concrete",
            (ConcreteBase, cls),
            dict(
                __slots__=_ur.DatDict(cls._yield_slots()),
                _get_ptolemaic_class=(lambda: cls),
                _clsmutable=_Switch(True),
                _clsiscosmic=False,
                ),
            )

    @classmethod
    def create_concrete(cls, /):
        return type(*cls.pre_create_concrete())

    ### Object creation:

    def __initialise__(self, /):
        self.__init__()
        self.mutable = False
        try:
            innerobjs = self._innerobjs
        except AttributeError:
            pass
        else:
            for name, obj in innerobjs.items():
                obj.__initialise__()
            object.__delattr__(self, '_innerobjs')

    @classmethod
    def _instantiate_(cls, params: tuple = (), /):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(True)
        object.__setattr__(obj, '_mutable', switch)
        obj._pyhash = _reseed.rdigits(16)
        obj.params = params
        return obj

    @classmethod
    def __instantiate__(cls, params: tuple = (), /):
        return cls._instantiate_(_ptolemaic.convert(params))

    @classmethod
    def _construct_(cls, params: tuple = (), /):
        obj = cls.__instantiate__(params)
        obj.__corpus__ = obj.__relname__ = None
        obj.__initialise__()
        return obj

    @classmethod
    def __class_alt_call__(cls, /, *args, **kwargs):
        return cls.__instantiate__(tuple(
            cls.__parameterise__(*args, **kwargs)
            .__dict__.values()
            ))

    @property
    def __cosmic__(self, /):
        return self.__corpus__ is None

    ### Storage:

    def __setattr__(self, name, val, /):
        if self.mutable:
            if not name.startswith('_'):
                val = _ptolemaic.convert(val)
            object.__setattr__(self, name, val)
        else:
            raise RuntimeError("Cannot alter value while immutable.")

    def __delattr__(self, name, /):
        if self.mutable:
            object.__delattr__(self, name)
        else:
            raise RuntimeError("Cannot alter value while immutable.")


    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def mutable(self, /):
        return self._mutable

    @mutable.setter
    def mutable(self, value, /):
        self.mutable.toggle(value)

    ### Representations:

    def _root_repr(self, /):
        return self.__ptolemaic_class__.__qualname__

    @property
    # @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    def _content_repr(self, /):
        raise NotImplementedError

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return repr(self.params)

    def __repr__(self, /):
        if self.__cosmic__:
            return f"<{self.rootrepr}, id={id(self)}>"
        return f"{self.__corpus__}.{self.__relname__}"

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def __taphonomise__(self, taph, /):
        if self.__cosmic__:
            return taph.getitem_epitaph(
                self.__ptolemaic_class__, tuple(self.params)
                )
        return taph.getattr_epitaph(self.__corpus__, self.__relname__)

    @property
    def taphonomy(self, /):
        return self.__ptolemaic_class__.taphonomy

    @property
    def epitaph(self, /):
        return self.taphonomy[self]

    def __reduce__(self, /):
        return self.epitaph, ()

    @property
    def hexcode(self, /):
        return self.epitaph.hexcode

    @property
    def hashint(self, /):
        return self.epitaph.hashint

    @property
    def hashID(self, /):
        return self.epitaph.hashID

    def __eq__(self, other, /):
        return hash(self) == hash(other)

    def __lt__(self, other, /):
        if isinstance(other, _OusiaBase_):
            other = other.hashint
        return self.hashint < other

    def __gt__(self, other, /):
        if isinstance(other, _OusiaBase_):
            other = other.hashint
        return self.hashint < other

    def __hash__(self, /):
        return object.__getattribute__(self, '_pyhash')

    @property
    def __ptolemaic_class__(self, /):
        return type(self)._get_ptolemaic_class()


###############################################################################
###############################################################################



#     @property
#     # @_caching.weak_cache()
#     def __dict__(self, /):
#         try:
#             out = super().__getattribute__('_sessioncacheref')()
#             if out is None:
#                 raise AttributeError
#             return out
#         except AttributeError:
#             out = _FOCUS.request_session_storer(self)
#             try:
#                 super().__setattr__('_sessioncacheref', _weakref.ref(out))
#             except AttributeError:
#                 raise RuntimeError(
#                     "Could not set the session cache on this object."
#                     )
#             return out

#     def reset(self, /):
#         self.__dict__.clear()
#         for dep in self.dependants:
#             dep.reset()

#     def __getattr__(self, name, /):
#         typ = type(self)
#         try:
#             meth = typ._getters_[name]
#         except AttributeError as exc:
#             raise RuntimeError from exc
#         except KeyError:
#             pass
#         else:
#             val = meth(self, name)
#             if not name.startswith('_'):
#                 val = type(self).param_convert(val)
#             object.__setattr__(self, name, val)
#             return val
#         if name in typ.__slots__:
#             raise AttributeError(name)
#         try:
#             return object.__getattribute__(self, '__dict__')[name]
#         except AttributeError as exc:
#             raise RuntimeError from exc
#         except KeyError as exc:
#             raise AttributeError from exc

#     def __setattr__(self, name, val, /):
#         typ = type(self)
#         if not name.startswith('_'):
#             val = typ.param_convert(val)
#         try:
#             meth = typ._setters_[name]
#         except AttributeError as exc:
#             raise RuntimeError from exc
#         except KeyError:
#             if name in typ.__slots__:
#                 if self.mutable:
#                     object.__setattr__(self, name, val)
#                 else:
#                     raise AttributeError(
#                         name, "Cannot alter slot while frozen."
#                         )
#             else:
#                 try:
#                     super().__setattr__(name, val)
#                 except AttributeError:
#                     try:
#                         object.__getattribute__(self, '__dict__')[name] = val
#                     except AttributeError as exc:
#                         raise RuntimeError from exc
#         else:
#             meth(self, name, val)

#     def __delattr__(self, name, /):
#         typ = type(self)
#         try:
#             meth = typ._deleters_[name]
#         except AttributeError as exc:
#             raise RuntimeError from exc
#         except KeyError:
#             if name in typ.__slots__:
#                 if self.mutable:
#                     object.__delattr__(self, name)
#                 else:
#                     try:
#                         super().__delattr__(name, val)
#                     except AttributeError:
#                         try:
#                             del object.__getattribute__(
#                                 self, '__dict__'
#                                 )[name]
#                         except AttributeError as exc:
#                             raise RuntimeError from exc
#                         except KeyError as exc:
#                             raise AttributeError from exc
#         else:
#             meth(self, name)

#     @property
#     def dependants(self, /):
#         return tuple(sorted(self._dependants))

#     def add_dependant(self, other, /):
#         self._dependants.add(other)

    # @property
    # @_caching.weak_cache()
    # def drawer(self, /):
    #     return _FOCUS.request_bureau_storer(self)
