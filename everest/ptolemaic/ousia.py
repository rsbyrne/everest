###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import itertools as _itertools
import inspect as _inspect

from everest.utilities import reseed as _reseed
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur
from everest.switch import Switch as _Switch

from .urgon import Urgon as _Urgon, SmartAttr as _SmartAttr


class Organ(_SmartAttr):
    ...


class Prop(_SmartAttr):
    ...


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


class Ousia(_Urgon):

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
        yield '__req_slots__', list, _ur.PrimitiveUniTuple

    @classmethod
    def handle_slots(meta, body, slots, /):
        body['__req_slots__'].extend(slots)


# @_BindableObject.register
class _OusiaBase_(metaclass=Ousia):

    __slots__ = (
        '__weakref__',
        '_mutable', '_pyhash', '_sessioncacheref', '_epitaph',
        '_dependants', '_notions', '_organs',
        '__corpus__', '__relname__',
        )

    ### Descriptor behaviours for class and instance:

    @classmethod
    def _get_ligatures(cls, corpus, /):
        signature = _inspect.signature(cls)
        bound = signature.bind_partial()
        bound.apply_defaults()
        arguments = bound.arguments
        for key in signature.parameters:
            try:
                arguments[key] = getattr(corpus, key)
            except AttributeError:
                arguments.setdefault(key, signature.empty)
        return tuple(arguments.values())

    @classmethod
    def __prop_get__(cls, instance, name, /):
        return cls[cls._get_ligatures(instance)]

    @classmethod
    def __organ_get__(cls, instance, name, /):
        out = cls.instantiate(cls._get_ligatures(instance))
        out.__set_name__(instance, name)
        return out

    def __set_name__(self, owner, name, /):
        if self.mutable:
            self.__corpus__ = owner
            self.__relname__ = name
            self.initialise()

    ## Configuring the class:

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from cls.__req_slots__
        yield from cls.__props__
        yield from cls.__organs__

    @classmethod
    def pre_create_concrete(cls, /):
        cls = cls.__ptolemaic_class__
        return (
            f"{cls.__name__}_Concrete",
            (ConcreteBase, cls),
            dict(
                __slots__=tuple(sorted(set(cls._yield_concrete_slots()))),
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

    def __getattr__(self, name, /):
        if name in self.__getattribute__('__slots__'):
            val = getattr(super(type(self), self), name)
            super().__setattr__(name, val)
            return val
        try:
            return self.__dict__[name]
        except KeyError as exc:
            raise AttributeError from exc

    def __setattr__(self, name, val, /):
        if name in self.__getattribute__('__slots__'):
            if not self.__getattribute__('_mutable'):
                raise AttributeError(
                    name, "Cannot alter slot while frozen."
                    )
            if not name.startswith('_'):
                type(self).param_convert(val)
                try:
                    setname = val.__set_name__
                except AttributeError:
                    pass
                else:
                    setname(self, name)
            super().__setattr__(name, val)
            return
        try:
            super().__setattr__(name, val)
        except AttributeError:
            if not name.startswith('_'):
                type(self).param_convert(val)
            self.__getattribute__('__dict__')[name] = val

    def __delattr__(self, name, /):
        if name in self.__getattribute__('__slots__'):
            if not self.__getattribute__('_mutable'):
                raise AttributeError(
                    name, "Cannot alter slot while frozen."
                    )
        try:
            super().__delattr__(name)
        except AttributeError:
            dct = self.__getattribute__('__dict__')
            try:
                del dct[name]
            except KeyError as exc:
                raise AttributeError from exc

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

#     @property
#     def dependants(self, /):
#         return tuple(sorted(self._dependants))

#     def add_dependant(self, other, /):
#         self._dependants.add(other)

    def reset(self, /):
        self.__dict__.clear()
        for dep in self.dependants:
            dep.reset()

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
        return f"<{self.rootrepr}, id={id(self)}>"

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
