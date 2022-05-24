###############################################################################
''''''
###############################################################################


import abc as _abc

import weakref as _weakref
from collections import abc as _collabc

from everest.utilities import pretty as _pretty, reseed as _reseed
from everest.utilities.switch import Switch as _Switch
from everest.bureau import FOCUS as _FOCUS
from everest import ur as _ur

from .essence import Essence as _Essence


class ConcreteMeta:

    @classmethod
    def __meta_call__(meta, basecls, /):
        assert not hasattr(basecls, 'Construct')
        if not isinstance(basecls, type):
            raise TypeError(
                "ConcreteMeta only accepts one argument:"
                " the class to be concreted."
                )
        if isinstance(basecls, ConcreteMeta):
            raise TypeError("Cannot subclass a Concrete type.")
        return super().__class_construct__(*basecls.pre_create_concrete())

    @property
    def __ptolemaic_class__(cls, /):
        return cls._basecls

    @property
    def __signature__(cls, /):
        return cls.__ptolemaic_class__.__signature__

    def __call__(cls, /):
        raise NotImplementedError

    @classmethod
    def __meta_init__(meta, /):
        pass


class Ousia(_Essence):

    @classmethod
    def concretemeta_namespace(meta, /):
        return {}

    @classmethod
    def __meta_init__(meta, /):
        super().__meta_init__()
        meta.ConcreteMeta = type(
            f"{meta.__name__}_ConcreteMeta",
            (ConcreteMeta, meta),
            meta.concretemeta_namespace(),
            )

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with cls.mutable:
            cls.Concrete = cls.ConcreteMeta(cls)

    @property
    def arity(cls, /):
        return len(cls.Params._fields)


@_ur.Dat.register
class OusiaBase(metaclass=Ousia):

    MERGENAMES = ('__req_slots__',)
    __req_slots__ = (
        '__weakref__',
        'freezeattr',
        'params',
        '_pyhash',
        '_sessioncacheref',
        '_epitaph',
        )     

    ## Configuring the class:

    @classmethod
    def _yield_concrete_slots(cls, /):
        yield from cls.__req_slots__

    @classmethod
    def pre_create_concrete(cls, /):
        return (
            f"Concrete_{cls.__ptolemaic_class__.__name__}",
            (cls,),
            dict(
                __slots__=tuple(sorted(set(cls._yield_concrete_slots()))),
                _basecls=cls,
                __class_init__=lambda: None,
                ),
            )

    ### Object creation:

    def initialise(self, params, /):
        object.__setattr__(self, '_pyhash', _reseed.rdigits(16))
        switch = _Switch(False)
        object.__setattr__(self, 'freezeattr', switch)
        for key, val in params.items():
            setattr(self, key, val)
        self.__init__()
        switch.toggle(True)

    @classmethod
    def parameterise(cls, /, *args, **kwargs) -> _collabc.Mapping:
        return dict(*args, **kwargs)

    @classmethod
    def instantiate(cls, params, /):
        Concrete = cls.Concrete
        obj = Concrete.__new__(Concrete)
        obj.initialise(params)
        return obj

    @classmethod
    def __class_call__(cls, /, *args, **kwargs):
        return cls.instantiate(cls.parameterise(*args, **kwargs))

    ### Some aliases:

    @property
    def __ptolemaic_class__(self, /):
        return self.__class__.__ptolemaic_class__

    @property
    def taphonomy(self, /):
        return self.__ptolemaic_class__.taphonomy

    ### Storage:

    @property
    # @_caching.weak_cache()
    def _sessioncache(self, /):
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
        if name in self.__slots__:
            raise AttributeError(name)
        try:
            return self._sessioncache[name]
        except KeyError as exc:
            raise AttributeError from exc

    def __setattr__(self, name, val, /):
        if self.freezeattr:
            if name in self.__slots__:
                raise AttributeError(name)
        else:
            try:
                return super().__setattr__(name, val)
            except AttributeError:
                pass
        self._sessioncache[name] = val

    def __delattr__(self, name, val, /):
        if self.freezeattr:
            if name in self.__slots__:
                raise AttributeError(name)
        else:
            try:
                return super().__delattr__(name)
            except AttributeError:
                pass
        try:
            del self._sessioncache[name]
        except KeyError as exc:
            raise AttributeError from exc

    ### Representations:

    def _root_repr(self, /):
        return self.__ptolemaic_class__.__qualname__

    @property
    # @_caching.soft_cache()
    def rootrepr(self, /):
        return self._root_repr()

    def __repr__(self, /):
        return f"<{self.rootrepr}, id={id(self)},"

    @_abc.abstractmethod
    def make_epitaph(self, /):
        raise NotImplementedError

    @property
    def epitaph(self, /):
        try:
            return object.__getattribute__(self, '_epitaph')
        except AttributeError:
            with self.mutable:
                try:
                    obj = self._epitaph = self.make_epitaph()
                except Exception as exc:
                    raise RuntimeError from exc
                return obj

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


# @OusiaLike.register
# class Tuuple(OusiaLike, tuple):

#     def __new__(cls, iterable=(), /):
#         return super().__new__(cls, map(convert, iterable))

#     def __repr__(self, /):
#         return f"Tuuple{super().__repr__()}"

#     @property
#     def epitaph(self, /):
#         return OusiaBase.taphonomy.callsig_epitaph(type(self), tuple(self))


# class Binding(dict, metaclass=Ousia):

#     def __init__(self, /, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.update({convert(key): convert(val) for key, val in self.items()})

#     @property
#     def __setitem__(self, /):
#         if self.freezeattr:
#             raise NotImplementedError
#         return super().__setitem__

#     @property
#     def __delitem__(self, /):
#         if self.freezeattr:
#             raise NotImplementedError
#         return super().__delitem__

#     def __repr__(self, /):
#         valpairs = ', '.join(map(':'.join, zip(
#             map(repr, self),
#             map(repr, self.values()),
#             )))
#         return f"<{self.__ptolemaic_class__}{{{valpairs}}}>"

#     def _repr_pretty_(self, p, cycle, root=None):
#         if root is None:
#             root = self.__ptolemaic_class__.__qualname__
#         _pretty.pretty_dict(self, p, cycle, root=root)

#     def make_epitaph(self, /):
#         ptolcls = self.__ptolemaic_class__
#         return ptolcls.taphonomy.callsig_epitaph(ptolcls, dict(self))
