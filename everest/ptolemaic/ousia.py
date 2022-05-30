###############################################################################
''''''
###############################################################################


import abc as _abc
import weakref as _weakref
import itertools as _itertools
from collections import abc as _collabc

from everest.utilities import pretty as _pretty, reseed as _reseed
from everest.utilities.switch import Switch as _Switch
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from .essence import Essence as _Essence


class Ousia(_Essence):

    @property
    def Concrete(cls, /):
        try:
            return cls.__dict__['_Concrete']
        except KeyError:
            with cls.mutable:
                out = cls._Concrete = cls.create_concrete()
            return out

    # @property
    # def Organ(cls, /):
    #     try:
    #         return cls._Organ
    #     except AttributeError:
    #         with cls.mutable:
    #             out = cls._Organ = type(*cls.pre_create_organ())
    #         return out


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


@_ur.Dat.register
class OusiaBase(metaclass=Ousia):

    MERGENAMES = ('__req_slots__', '__var_slots__')
    __req_slots__ = (
        '__weakref__',
        'freezeattr', '_pyhash', '_sessioncacheref', '_epitaph',
        'params',
        )

    ## Configuring the class:

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from ()

    @classmethod
    def pre_create_concrete(cls, /):
        return (
            f"{cls.__ptolemaic_class__.__name__}_Concrete",
            (ConcreteBase, cls),
            dict(
                __slots__=tuple(sorted(set(_itertools.chain(
                    cls.__req_slots__,
                    cls._yield_concrete_slots(),
                    )))),
                __ptolemaic_class__=cls,
                __class_deep_init__=lambda: None,
                ),
            )

    @classmethod
    def create_concrete(cls, /):
        return type(*cls.pre_create_concrete())

    ### Object creation:

    @classmethod
    def construct(cls,
            params: _collabc.Mapping = _ur.DatDict(), /,    
            *args, _epitaph=None, **kwargs,
            ):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        switch = _Switch(False)
        object.__setattr__(obj, 'freezeattr', switch)
        obj._epitaph = _epitaph
        obj._pyhash = _reseed.rdigits(16)
        obj.params = params
        for key, val in params.items():
            setattr(obj, key, val)
        obj.__init__(*args, **kwargs)
        switch.toggle(True)
        return obj

    @classmethod
    def __class_call__(cls, /, **params):
        return cls.construct(_ur.DatDict(params))

    # Special-cased, so no need for @classmethod
    def __class_getitem__(cls, params, /):
        return cls.construct(_ur.DatDict(params))

    ### Storage:

    @property
    # @_caching.weak_cache()
    def __vardict__(self, /):
        try:
            out = object.__getattribute__(self, '_sessioncacheref')()
            if out is None:
                raise AttributeError
            return out
        except AttributeError:
            out = _FOCUS.request_session_storer(self)
            try:
                object.__setattr__(
                    self, '_sessioncacheref', _weakref.ref(out)
                    )
            except AttributeError:
                raise RuntimeError(
                    "Could not set the session cache on this object."
                    )
            return out

    # @property
    # @_caching.weak_cache()
    # def drawer(self, /):
    #     return _FOCUS.request_bureau_storer(self)

    ### Implementing the attribute-freezing behaviour for instances:

    @property
    def mutable(self, /):
        return self.freezeattr.as_(False)

    def __getattr__(self, name, /):
        if name in self.__var_slots__:
            try:
                return self.__vardict__[name]
            except KeyError as exc:
                raise AttributeError from exc
        raise AttributeError(name)

    def __setattr__(self, name, val, /):
        if name in self.__var_slots__:
            self.__vardict__[name] = val
        if name in self.__slots__:
            if self.freezeattr:
                raise AttributeError(name)
        super().__setattr__(name, val)

    def __delattr__(self, name, /):
        if name in self.__var_slots__:
            try:
                del self.__vardict__[name]
            except KeyError as exc:
                raise AttributeError from exc
        if name in self.__slots__:
            if self.freezeattr:
                raise AttributeError(name)
        super().__delattr__(name)

    ### Representations:

    def _root_repr(self, /):
        return self.__ptolemaic_class__.__qualname__

    @property
    # @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    def __repr__(self, /):
        return f"<{self.rootrepr}, id={id(self)}>"

    def make_epitaph(self, /):
        return cls.taphonomy.getitem_epitaph(cls, dict(params))

    @property
    def epitaph(self, /):
        epi = self._epitaph
        if epi is None:
            epi = self.make_epitaph()
            with self.mutable:
                self._epitaph = epi
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


###############################################################################
###############################################################################
