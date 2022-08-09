###############################################################################
''''''
###############################################################################


import abc as _abc
import itertools as _itertools
from collections import abc as _collabc

from everest.utilities import reseed as _reseed, pretty as _pretty
from everest.bureau import FOCUS as _FOCUS
from everest.switch import Switch as _Switch
from everest import ur as _ur

from . import ptolemaic as _ptolemaic
from .urgon import Urgon as _Urgon


class ConcreteBase:

    __slots__ = ()

    for methname in (
            '__class_call__',
            '_create_concrete', '_pre_create_concrete',
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

    @classmethod
    def convert(meta, arg, /):
        try:
            return super().convert(arg)
        except TypeError:
            try:
                colltyp = Pentheros[type(arg)]
            except KeyError as exc:
                raise TypeError from exc
            return colltyp(arg)

    @property
    def Concrete(cls, /):
        cls = cls.__ptolemaic_class__
        try:
            return cls.__dict__['_Concrete']
        except KeyError:
            with cls.__mutable__:
                out = cls._Concrete = _abc.ABCMeta.__new__(
                    type(cls), *cls._pre_create_concrete()
                    )
                out.__mutable__ = False
            return out

    @classmethod
    def _yield_mergenames(meta, /):
        yield from super()._yield_mergenames()
        yield '__req_slots__', (dict, dict)

    @classmethod
    def handle_slots(meta, body, slots, /):
        if not isinstance(slots, _collabc.Mapping):
            slots = zip(slots, _itertools.repeat(None))
        body['__req_slots__'].update(slots)


@_ptolemaic.Case.register
class _OusiaBase_(metaclass=Ousia):

    __slots__ = (
        '__weakref__',
        '__params__', '_mutable', '_pyhash', '_sessioncacheref',
        '_innerobjs', '__corpus__', '__relname__', '_instancesignature',
        )

    @property
    def __progenitor__(self, /):
        return self.__ptolemaic_class__

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

    def _register_innerobj(self, name, obj, /):
        _ptolemaic.configure_as_innerobj(obj, self, name)
        if self.__mutable__:
            self._innerobjs[name] = obj
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
    def _pre_create_concrete(cls, /):
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
    def _create_concrete(cls, /):
        return type(*cls._pre_create_concrete())

    ### Object creation:

    def __initialise__(self, /):
        self.__init__()
        innerobjs = self._innerobjs
        for name, obj in innerobjs.items():
            obj.__initialise__()
        for obj in innerobjs.values():
            obj.__mutable__ = False
        del self._innerobjs

    @classmethod
    def _instantiate_(cls, params: tuple = (), /):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(True)
        object.__setattr__(obj, '_mutable', switch)
        obj._pyhash = _reseed.rdigits(16)
        obj.__params__ = params
        obj._innerobjs = {}
        return obj

    @classmethod
    def __instantiate__(cls, params: tuple = (), /):
        return cls._instantiate_(cls.___parameterise__(params))

    @classmethod
    def _construct_(cls, params: tuple = (), /):
        obj = cls.__instantiate__(params)
        obj.__corpus__ = obj.__relname__ = None
        obj.__initialise__()
        obj.__mutable__ = False
        return obj

    @classmethod
    def __class_alt_call__(cls, /, *args, **kwargs):
        return cls.__instantiate__(
            cls.___parameterise__(cls._parameterise_(*args, **kwargs))
            )

    ### Storage:

    def __setattr__(self, name, val, /):
        if self.__mutable__:
            if not name.startswith('_'):
                val = self.__ptolemaic_class__.convert(val)
            object.__setattr__(self, name, val)
            return val
        raise RuntimeError("Cannot alter value while immutable.")

    def __delattr__(self, name, /):
        if self.__mutable__:
            object.__delattr__(self, name)
        else:
            raise RuntimeError("Cannot alter value while immutable.")


    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def __mutable__(self, /):
        return self._mutable

    @__mutable__.setter
    def __mutable__(self, value, /):
        self.__mutable__.toggle(value)

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
        return repr(self.__params__)

    def __repr__(self, /):
        if self.__corpus__ is None:
            return f"<{self.rootrepr}, id={id(self)}>"
        return f"{self.__corpus__}.{self.__relname__}"

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    def __taphonomise__(self, taph, /):
        if self.__corpus__ is None:
            return taph.getitem_epitaph(
                self.__ptolemaic_class__, tuple(self.__params__)
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

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_tuple(self.__params__, p, cycle, root=root)


class Pentheros(Ousia):

    _colltyps = {}

    @classmethod
    def __meta_getitem__(meta, arg, /):
        return meta._colltyps[arg]


@_collabc.Collection.register
class _PentherosBase_(metaclass=Pentheros):

    __slots__ = ('_content',)

    __content_type__ = None
    __content_meths__ = ()
    _types = {}

    @classmethod
    def __class_init__(cls, /):
        super().__class_init__()
        if cls is not __class__:
            if (typ := cls.__content_type__) not in (dct := Pentheros._colltyps):
                dct[typ] = cls

    def __init__(self, /):
        self._content = self._make_content()

    @_abc.abstractmethod
    def _make_content(self, /):
        raise NotImplementedError


@_collabc.Sequence.register
class Tuuple(metaclass=Pentheros):

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        try:
            return tuple(*args, **kwargs)
        except TypeError:
            return tuple(args, **kwargs)

    def _make_content(self, /):
        return self.__params__

    __content_type__ = tuple
    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', '__reversed__', 'index', 'count',
        )

    with escaped('methname'):
        for methname in __content_meths__:
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self._content.{methname}",
                )))


@_collabc.Mapping.register
class Binding(metaclass=Pentheros):

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        dct = dict(*args, **kwargs)
        return tuple(map(Tuuple, (dct.keys(), dct.values())))

    def _make_content(self, /):
        return _ur.DatDict(zip(*self.__params__))

    __content_type__ = dict
    __content_meths__ = (
        '__len__', '__contains__', '__iter__',
        '__getitem__', 'keys', 'items', 'values', 'get',
        )

    with escaped('methname'):
        for methname in __content_meths__:
            exec('\n'.join((
                f"@property",
                f"def {methname}(self, /):",
                f"    return self._content.{methname}",
                )))

    def __init__(self, /):
        self._content = _ur.DatDict(zip(*self.__params__))

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_dict(self._content, p, cycle, root=root)


class Kwargs(Binding):

    @classmethod
    def _parameterise_(cls, /, *args, **kwargs):
        keys, vals = super()._parameterise_(*args, **kwargs)
        if not all(type(key) is str for key in keys):
            raise ValueError(
                f"Only string keys are permitted "
                f"as inputs to {__class__.__name__}."
                )
        return keys, vals

    def _repr_pretty_(self, p, cycle, root=None):
        if root is None:
            root = self.__ptolemaic_class__.__qualname__
        _pretty.pretty_kwargs(self._content, p, cycle, root=root)

    def __taphonomise__(self, taph, /):
        return taph.callsig_epitaph(self.__ptolemaic_class__, **self)


# @_collabc.Sequence.register
# class Arraay(Collection):

#     __content_type__ = _ur.DatArray
#     __content_meths__ = (
#         '__len__', '__contains__', '__iter__',
#         '__getitem__', 'dtype', 'shape',
#         '__reversed__', 'index', 'count',
#         )

#     with escaped('methname'):
#         for methname in __content_meths__:
#             exec('\n'.join((
#                 f"@property",
#                 f"def {methname}(self, /):",
#                 f"    return self._content.{methname}",
#                 )))


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
#                 if self.__mutable__:
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
#                 if self.__mutable__:
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
