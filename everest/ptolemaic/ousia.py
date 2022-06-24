###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import itertools as _itertools
import types as _types
import functools as _functools
from collections import abc as _collabc, ChainMap as _ChainMap

from everest.armature import Armature as _Armature
from everest.utilities import reseed as _reseed
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur
from everest.switch import Switch as _Switch

from . import ptolemaic as _ptolemaic
from .urgon import Urgon as _Urgon
from .eidos import Eidos as _Eidos, SmartAttr as _SmartAttr
from .utilities import get_ligatures as _get_ligatures


class Organ(_SmartAttr):

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        content = params.content
        if not isinstance(content, _ptolemaic.Kind):
            raise ValueError(content)
        if params.hint is None:
            params.hint = content
        return params


def ligated_function(instance, name, /):
    func = getattr(instance.__ptolemaic_class__, name).__get__(instance)
    bound = _get_ligatures(func, instance)
    return func(*bound.args, **bound.kwargs)


class Prop(_SmartAttr):

    @classmethod
    def parameterise(cls, /, *args, **kwargs):
        params = super().parameterise(*args, **kwargs)
        if params.hint is None:
            content = params.content
            if isinstance(content, _ptolemaic.Kind):
                params.hint = content
            elif isinstance(content, _types.FunctionType):
                params.hint = content.__annotations__.get('return', None)
        return params

    @classmethod
    def _get_getter_(cls, obj):
        if isinstance(obj, _ptolemaic.Kind):
            return super()._get_getter_(obj)
        if isinstance(obj, _types.FunctionType):
            return ligated_function
        raise TypeError(type(obj))


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

    @classmethod
    def __mro_entries__(cls, bases: tuple, /):
        return (cls.__ptolemaic_class__,)


@_ptolemaic.Kind.register
class Ousia(_Urgon, _Eidos):

    @classmethod
    def _yield_smartattrtypes(meta, /):
        yield from super()._yield_smartattrtypes()
        yield Organ
        yield Prop

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
    def _yield_mergenames(meta, body, /):
        yield from super()._yield_mergenames(body)
        yield '__req_slots__', dict, _ptolemaic.PtolDict

    @classmethod
    def handle_slots(meta, body, slots, /):
        if not isinstance(slots, _collabc.Mapping):
            slots = zip(slots, _itertools.repeat(None))
        body['__req_slots__'].update(slots)

    @classmethod
    def process_shadow(meta, body, name, val, /):
        exec('\n'.join((
            f"def {name}(self, {', '.join((sh.name for sh in val.shades))}):",
            f"    return {val.evalstr}",
            )))
        func = eval(name)
        func.__module__ = body['__module__']
        func.__qualname__ = body['__qualname__'] + '.' + name
        body[name] = body['prop'](func)


@_ptolemaic.Case.register
class _OusiaBase_(metaclass=Ousia):

    __slots__ = (
        '__weakref__',
        '_mutable', '_pyhash', '_sessioncacheref', '_epitaph',
        '__corpus__', '__relname__',
        )

    ### Descriptor behaviours for class and instance:

    @classmethod
    def __prop_get__(cls, instance, name, /):
        return cls[
            tuple(_get_ligatures(cls, instance).arguments.values())
            ]

    @classmethod
    def __organ_get__(cls, instance, name, /):
        out = cls.instantiate(
            tuple(_get_ligatures(cls, instance).arguments.values())
            )
        out.__set_name__(instance, name)
        return out

    def __set_name__(self, owner, name, /):
        if self.mutable:
            self.__corpus__ = owner
            self.__relname__ = name
            self.initialise()

    ## Configuring the class:

    @classmethod
    def _yield_slot_sources(cls, /):
        yield cls.__req_slots__
        yield cls.__props__
        yield cls.__organs__

    @classmethod
    def pre_create_concrete(cls, /):
        cls = cls.__ptolemaic_class__
        return (
            f"{cls.__name__}_Concrete",
            (ConcreteBase, cls),
            dict(
                __slots__=_ChainMap(*cls._yield_slot_sources()),
                _get_ptolemaic_class=(lambda: cls),
                _clsmutable=_Switch(True),
                _clsiscosmic=False,
                ),
            )

    @classmethod
    def create_concrete(cls, /):
        return type(*cls.pre_create_concrete())

    ### Object creation:

    def initialise(self, /):
        self.__init__()
        self.mutable = False

    @classmethod
    def _instantiate_(cls, params: tuple, /):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(True)
        object.__setattr__(obj, '_mutable', switch)
        obj._pyhash = _reseed.rdigits(16)
        obj.params = params
        return obj

    @classmethod
    def instantiate(cls, params: tuple, /):
        return cls._instantiate_(tuple(map(cls.param_convert, params)))

    @classmethod
    def _construct_(cls, params: tuple, /):
        obj = cls.instantiate(params)
        obj.__corpus__ = obj.__relname__ = None
        obj.initialise()
        return obj

    @classmethod
    def construct(cls, params: tuple, /):
        return cls._construct_(tuple(map(cls.param_convert, params)))

    @property
    def __cosmic__(self, /):
        return self.__corpus__ is None

    ### Storage:

    @property
    # @_caching.weak_cache()
    def __dict__(self, /):
        try:
            out = super().__getattribute__('_sessioncacheref')()
            if out is None:
                raise AttributeError
            return out
        except AttributeError:
            out = _FOCUS.request_session_storer(self)
            try:
                super().__setattr__('_sessioncacheref', _weakref.ref(out))
            except AttributeError:
                raise RuntimeError(
                    "Could not set the session cache on this object."
                    )
            return out

    def reset(self, /):
        self.__dict__.clear()
        for dep in self.dependants:
            dep.reset()

    def __getattr__(self, name, /):
        typ = type(self)
        try:
            meth = typ._getters_[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError:
            pass
        else:
            val = meth(self, name)
            if not name.startswith('_'):
                val = type(self).param_convert(val)
            object.__setattr__(self, name, val)
            return val
        if name in typ.__slots__:
            raise AttributeError(name)
        try:
            return object.__getattribute__(self, '__dict__')[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError as exc:
            raise AttributeError from exc

    def __setattr__(self, name, val, /):
        typ = type(self)
        if not name.startswith('_'):
            val = typ.param_convert(val)
        try:
            meth = typ._setters_[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError:
            if name in typ.__slots__:
                if self.mutable:
                    object.__setattr__(self, name, val)
                else:
                    raise AttributeError(
                        name, "Cannot alter slot while frozen."
                        )
            else:
                try:
                    super().__setattr__(name, val)
                except AttributeError:
                    try:
                        object.__getattribute__(self, '__dict__')[name] = val
                    except AttributeError as exc:
                        raise RuntimeError from exc
        else:
            meth(self, name, val)

    def __delattr__(self, name, /):
        typ = type(self)
        try:
            meth = typ._deleters_[name]
        except AttributeError as exc:
            raise RuntimeError from exc
        except KeyError:
            if name in typ.__slots__:
                if self.mutable:
                    object.__delattr__(self, name)
                else:
                    try:
                        super().__delattr__(name, val)
                    except AttributeError:
                        try:
                            del object.__getattribute__(self, '__dict__')[name]
                        except AttributeError as exc:
                            raise RuntimeError from exc
                        except KeyError as exc:
                            raise AttributeError from exc
        else:
            meth(self, name)

#     @property
#     def dependants(self, /):
#         return tuple(sorted(self._dependants))

#     def add_dependant(self, other, /):
#         self._dependants.add(other)

    # @property
    # @_caching.weak_cache()
    # def drawer(self, /):
    #     return _FOCUS.request_bureau_storer(self)

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

    @_abc.abstractmethod
    def _content_repr(self, /):
        raise NotImplementedError

    @property
    # @_caching.soft_cache()
    def contentrepr(self, /):
        return self._content_repr()

    def __repr__(self, /):
        if self.__cosmic__:
            return f"<{self.rootrepr}, id={id(self)}>"
        return f"{self.__corpus__}.{self.__relname__}"

    def __str__(self, /):
        return f"{self.rootrepr}({self.contentrepr})"

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    def epitaph(self, /):
        try:
            return self._epitaph
        except AttributeError:
            epi = self.make_epitaph()
            super().__setattr__(self, '_epitaph', epi)
            return epi

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
        return self.hashint < other

    def __gt__(self, other, /):
        return self.hashint < other

    def __hash__(self, /):
        return object.__getattribute__(self, '_pyhash')

    @property
    def __ptolemaic_class__(self, /):
        return type(self)._get_ptolemaic_class()


###############################################################################
###############################################################################
